import command.register_init_data as mod


if __name__ == '__main__':

    try:
        print('register init data')
        mod.register_init_data_staff()
        mod.register_init_data_car()
        mod.register_init_data_machine()
        mod.register_init_data_lease()
        mod.register_init_data_item()
        mod.register_init_data_dest()
        mod.register_init_data_customer()
    except Exception as e:
        print(e)
        raise
