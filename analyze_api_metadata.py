from Modules.osp_api_analyzer import OspApiAnalyzer

ospApiAnalyzer = OspApiAnalyzer()
ospApiAnalyzer.read_tables_from_file()
ospApiAnalyzer.evaluate_metadata()
