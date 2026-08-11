from src.textgrid_allignment import merge_all_tiers, match_files

# BATCH OUTPUT
files = match_files("data/drift_project/(4)Data/(1)First/output/first_1/en", "data/drift_project/(4)Data/(1)First/output/first_1/zh")
for file_id, files in files.items():
    output_name = "data/drift_project/(4)Data/(1)First/output/first_1/merged/" + files[0].name
    merge_all_tiers(str(files[0]), str(files[1]), output_name)

'''
# INDIVIDUAL OUTPUT
merge_all_tiers("data/test/output/P01_first/en/P01_first.TextGrid", "data/test/output/P01_first/ma/P01_first.TextGrid", "data/merged.TextGrid")
'''