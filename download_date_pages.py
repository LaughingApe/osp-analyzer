from Modules.osp_date_analyzer import OspDateAnalyzer

ospGuiAnalyzer = OspDateAnalyzer(table_limit = 100000, sleep_time = 1)
ospGuiAnalyzer.read_date_pages()