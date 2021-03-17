def accounting_numbers_to_ints(result_dict: dict):
    for key, acc_number in result_dict.items():
        number = acc_number.replace(",", "")
        result_dict[key] = int(number)
