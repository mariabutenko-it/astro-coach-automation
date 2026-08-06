from utils.data_loader import load_test_data


def test_load_test_data():

    data = load_test_data()

    assert data["users"]["default"]["username"] == "test_user"
    assert data["api"]["timeout"] == 10
