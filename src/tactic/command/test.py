def update_sobjects(changelist_file_path):
    try:
        saved_file_path = "//wfms/JootaProjects/SS17/Football/14970161-Predator Incurza TRX AG/"

        if changelist_file_path.find(saved_file_path) != -1:
            print changelist_file_path.find(saved_file_path)

    except Exception, err:
        raise err


if __name__ == "__main__":
    # Absolute path of a file in the sorted list of changelist files is passed as an argument to this script. # Absolute path of a file in the sorted list of changelist files is passed as an argument to this script.
    changelist_file_path = "//wfms/JootaProjects/SS17/Football/14970161-Predator Incurza TRX AG/14970161-EmptyJPrj.apr"
    update_sobjects(changelist_file_path)