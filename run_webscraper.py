from Modules.osp_webscraper import OspWebScraper

ospWebScraper = OspWebScraper(table_limit = 30, sleep_time = 2)
ospWebScraper.read_metadata()