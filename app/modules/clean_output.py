# clean output folder
import shutil


async def cleaner(output_folder):
    shutil.rmtree(output_folder, ignore_errors=True)
