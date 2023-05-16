from Modules.osp_api_analyzer import OspApiAnalyzer

ospApiAnalyzer = OspApiAnalyzer(table_limit = 1000000, sleep_time=1)
ospApiAnalyzer.read_categories()