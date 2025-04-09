import aiohttp
import asyncio
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from gcbot.port.adapter.sqlalchemy_resources.tables import groups_table


class GetCourseError(Exception):
    pass


class GetCourseHTTPError(GetCourseError):
    pass


class GetCourseAPIError(GetCourseError):
    pass


class DataProcessingError(GetCourseError):
    pass


async def get_export_id(group_id, access_key):
    url = f"https://workoutmila.ru/pl/api/account/groups/{group_id}/users?key={access_key}&status=active"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise GetCourseHTTPError(
                    f"[Group ID: {group_id}] Ошибка HTTP: {response.status} - {await response.text()}"
                )
            data = await response.json()
            if not data.get("success") or data.get("error"):
                error_msg = data.get("error_message", "Неизвестная ошибка")
                raise GetCourseAPIError(
                    f"[Group ID: {group_id}] Ошибка API: {error_msg}"
                )
            export_id = data.get("info", {}).get("export_id")
            if not export_id:
                raise DataProcessingError(
                    f"[Group ID: {group_id}] export_id не найден в ответе"
                )
            return export_id

async def get_items_from_export(export_id, access_key):
    url = f"https://workoutmila.ru/pl/api/account/exports/{export_id}?key={access_key}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise GetCourseHTTPError(
                    f"[Export ID: {export_id}] Ошибка HTTP: {response.status} - {await response.text()}"
                )
            data = await response.json()
            if not data.get("success") or data.get("error"):
                error_msg = data.get("error_message", "Неизвестная ошибка")
                raise GetCourseAPIError(
                    f"[Export ID: {export_id}] Ошибка API: {error_msg}"
                )
            items = data.get("info", {}).get("items")
            if not items:
                raise DataProcessingError(
                    f"[Export ID: {export_id}] items не найдены в ответе"
                )
            return items

async def process_group(group_id, access_key, delay_between_requests):
    export_id = await get_export_id(group_id, access_key)    
    await asyncio.sleep(delay_between_requests)
    items = await get_items_from_export(export_id, access_key)
    result = []
    for item in items:
        if len(item) < 30:
            raise DataProcessingError(
                f"[Group ID: {group_id}] Недостаточно элементов в списке: {item}"
            )
        email = item[1]
        group_id_value = item[30]
        result.append({"email": email.lower(), "group_id": group_id_value})
    return result

async def parse_gc(engine):
    group_ids = ["3088338", "2315673"]
    access_key = "qZ2MZ3kHUxzFZpp4JJvzBQOWeQd1f9hwafDixfBWoYbpQp7OCqcDu6H0PBDQbcqw2JC5LCAVKdK1epLPsFFopntOUHHxtODgQqSxhJlQkjCFvfYio1NCiy98g09p9hDT"
    delay_between_groups = 60

    while True:
        all_results = []
        try:
            print("Начало нового цикла обработки групп...")
            for group_id in group_ids:
                print(f"Обработка Group ID: {group_id}")
                group_results = await process_group(group_id, access_key, 60)
                if group_results:
                    all_results.extend(group_results)
                    print(f"[{group_id}] Добавлено {len(group_results)} записей")
                await asyncio.sleep(delay_between_groups)
            
            async with AsyncSession(engine) as session:
                async with session.begin():
                    await session.execute(sa.delete(groups_table).where(groups_table.c.group_id != 1))
                    await session.execute(sa.insert(groups_table).values(all_results))
                    await session.commit()
            
        except GetCourseError as e:
            print(f"Ошибка GetCourse: {e}")
        except Exception as e:
            print(f"Непредвиденная ошибка: {e}")
        finally:
            print("Ожидание 1 час 5 минут перед следующим циклом...")
            await asyncio.sleep(3900)