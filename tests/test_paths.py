from brasileirao_forecast import paths


def test_project_root_contains_pyproject():
    assert (paths.PROJECT_ROOT / "pyproject.toml").is_file()


def test_data_subdirs_live_under_data_dir():
    assert paths.RAW_DIR.parent == paths.DATA_DIR
    assert paths.PROCESSED_DIR.parent == paths.DATA_DIR
