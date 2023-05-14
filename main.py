from osp_reader import OSPReader

# scb = SCB('en', 'POP', 'IR', 'IRE', 'IRE010')
# #scb.set_query(ETHNICITY=['E_IND'], TIME=['2011','2016', '2020'])
# #print(scb.get_query())
# scb.get_data()
# scb_data = scb.get_data()
# scb_fetch = scb_data['data']
# print(scb_data)


ospReader = OSPReader()
ospReader.read_categories()
ospReader.print_categories_tables_with_extra_info()
ospReader.read_tables_from_file()
ospReader.evaluate_metadata()
