from db_bridges.mongo_bridge.collection_structure import CollectionStructure
from toolbox.date_tool import DateTool


class ThreeDaysStrategyDataCollection(CollectionStructure):
    def set_name(self):
        return 'threeDaysStrategyData'

    def set_unique_fields(self):
        return {
            'stockCode': str,
            'year': int,
            'month': int,
            'day': int,
            'intDate': int,
        }

    def set_data_fields(self):
        return {
            'd1AgoTradeVolume': 0,
            'd1AgoAmount': 0,
            'd1AgoOpeningPrice': 0.0,
            'd1AgoHighestPrice': 0.0,
            'd1AgoLowestPrice': 0.0,
            'd1AgoClosingPrice': 0.0,
            'd1AgoClosingDiff': 0.0,
            'd1AgoTransaction': 0,
            'd1AgoMaxDiff': 0.0,
            'd2AgoTradeVolume': 0,
            'd2AgoAmount': 0,
            'd2AgoOpeningPrice': 0.0,
            'd2AgoHighestPrice': 0.0,
            'd2AgoLowestPrice': 0.0,
            'd2AgoClosingPrice': 0.0,
            'd2AgoClosingDiff': 0.0,
            'd2AgoTransaction': 0,
            'd2AgoMaxDiff': 0.0,
            'd3AgoTradeVolume': 0,
            'd3AgoAmount': 0,
            'd3AgoOpeningPrice': 0.0,
            'd3AgoHighestPrice': 0.0,
            'd3AgoLowestPrice': 0.0,
            'd3AgoClosingPrice': 0.0,
            'd3AgoClosingDiff': 0.0,
            'd3AgoTransaction': 0,
            'd1AgoMaxDiff': 0.0,
            'dDayPriseRise': 0,
            'dDayClosingDiff': 0,
        }
