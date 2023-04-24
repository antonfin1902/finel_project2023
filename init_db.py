from tortoise import Tortoise , run_async
import settings as stg


async def init():
  try:
    await Tortoise.init(stg.TORTOISE_ORM)
  except Exception as e:
    print(f"init db Error:{e}")

  
  try:
    await  Tortoise.generate_schemas()
  except Exception as e:
    print(f"generate schemas to db Error:{e}")