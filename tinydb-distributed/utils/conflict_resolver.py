
# Hàm xử lý conflict giữa dữ liệu cũ và dữ liệu mới
def resolve_conflict(old_data, new_data):

    old_timestamp = old_data.get("timestamp", 0)

    new_timestamp = new_data.get("timestamp", 0)


    if new_timestamp > old_timestamp:

        return new_data

    return old_data

