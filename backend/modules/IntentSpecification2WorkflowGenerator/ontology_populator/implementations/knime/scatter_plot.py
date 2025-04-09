from common import *
from ..core import *
from .knime_implementation import KnimeImplementation, KnimeParameter, KnimeJSBundle, KnimeJSViewsFeature

scatterplot_visualizer_implementation = KnimeImplementation(

    name = "Scatter Plot Visualizer",
    algorithm = cb.ScatterPlot,
    parameters = [

        KnimeParameter("generateImage", XSD.boolean, True, 'generateImage', path="model"),
        KnimeParameter("Maximum Number of Rows", XSD.int, 2500, 'maxRows', path="model"),
        KnimeParameter("Selection Column Name", XSD.string, "Selected (Scatter Plot)", 'selectionColumnName', path="model"),
        KnimeParameter("Scatterplot X Axis Column", XSD.string, "$$SCATTERPLOT_XCOLUMN$$", 'xCol', path="model"), 
        KnimeParameter("Scatterplot Y Axis Column", XSD.string, "$$SCATTERPLOT_YCOLUMN$$", 'yCol', path="model"), 
        KnimeParameter("Report On Missing Values", XSD.boolean, True, 'reportOnMissingValues', path="model"), 
        KnimeParameter("X Axis Label", XSD.string, "", 'xAxisLabel', path="model"), 
        KnimeParameter("Y Axis Label", XSD.string, "", 'yAxisLabel', path="model"),
        KnimeParameter("X Axis Min", XSD.string, None, 'xAxisMin', path="model"),
        KnimeParameter("X Axis Max", XSD.string, None, 'xAxisMax', path="model"),
        KnimeParameter("Y Axis Min", XSD.string, None, 'yAxisMin', path="model"),
        KnimeParameter("Y Axis Max", XSD.string, None, 'yAxisMax', path="model"),
        KnimeParameter("Dot Size", XSD.string, "3", 'dot_size', path="model"),
        KnimeParameter("DTFI SettingsModelID", XSD.string, "SMID_datetime", 'SettingsModelID',
                       path="model/dateTimeFormats_Internals"),
        KnimeParameter("DTFI EnabledStatus", XSD.boolean, True, 'EnabledStatus',
                       path="model/dateTimeFormats_Internals"),
        KnimeParameter("Global Date Time Locale", XSD.string, "en", 'globalDateTimeLocale', path="model/dateTimeFormats"),
        KnimeParameter("GDTLI SettingsModelID", XSD.string, "SMID_string", 'SettingsModelID',
                       path="model/dateTimeFormats/globalDateTimeLocale_Internals"),
        KnimeParameter("GDTLI EnabledStatus", XSD.boolean, True, 'EnabledStatus',
                       path="model/dateTimeFormats/globalDateTimeLocale_Internals"),
        KnimeParameter("Global Date Format", XSD.string, "YYYY-MM-DD", 'globalDateFormat', path="model/dateTimeFormats"),
        KnimeParameter("GDFI SettingsModelID", XSD.string, "SMID_string", 'SettingsModelID',
                       path="model/dateTimeFormats/globalDateFormat_Internals"),
        KnimeParameter("GDFI EnabledStatus", XSD.boolean, True, 'EnabledStatus',
                       path="model/dateTimeFormats/globalDateFormat_Internals"),
        KnimeParameter("Global Local Date Format", XSD.string, "YYYY-MM-DD", 'globalLocalDateFormat', path="model/dateTimeFormats"), 
        KnimeParameter("GLDFI SettingsModelID", XSD.string, "SMID_string", 'SettingsModelID',
                       path="model/dateTimeFormats/globalLocalDateFormat_Internals"),
        KnimeParameter("GLDFI EnabledStatus", XSD.boolean, True, 'EnabledStatus',
                       path="model/dateTimeFormats/globalLocalDateFormat_Internals"),
        KnimeParameter("Global Local Date and Time Format", XSD.string, "YYYY-MM-DD", 'globalLocalDateTimeFormat', path="model/dateTimeFormats"), 
        KnimeParameter("GLDTI SettingsModelID", XSD.string, "SMID_string", 'SettingsModelID',
                       path="model/dateTimeFormats/globalLocalDateTimeFormat_Internals"),
        KnimeParameter("GLDTI EnabledStatus", XSD.boolean, True, 'EnabledStatus',
                       path="model/dateTimeFormats/globalLocalDateTimeFormat_Internals"),
        KnimeParameter("Global Local Time Format", XSD.string, "HH:mm:ss", 'globalLocalTimeFormat', path="model/dateTimeFormats"), 
        KnimeParameter("GLTFI SettingsModelID", XSD.string, "SMID_string", 'SettingsModelID',
                       path="model/dateTimeFormats/globalLocalTimeFormat_Internals"),
        KnimeParameter("GLTFI EnabledStatus", XSD.boolean, True, 'EnabledStatus',
                       path="model/dateTimeFormats/globalLocalTimeFormat_Internals"),
        KnimeParameter("Global Zoned Date and Time Format", XSD.string, "YYYY-MM-DD z", 'globalZonedDateTimeFormat', path="model/dateTimeFormats"), 
        KnimeParameter("GZDTI SettingsModelID", XSD.string, "SMID_string", 'SettingsModelID',
                       path="model/dateTimeFormats/globalZonedDateTimeFormat_Internals"),
        KnimeParameter("GZDTI EnabledStatus", XSD.boolean, True, 'EnabledStatus',
                       path="model/dateTimeFormats/globalZonedDateTimeFormat_Internals"),
        KnimeParameter("Time Zone", XSD.string, "Europe/Madrid", 'timezone', path="model/dateTimeFormats"), 
        KnimeParameter("TZI SettingsModelID", XSD.string, "SMID_string", 'SettingsModelID',
                       path="model/dateTimeFormats/timezone_Internals"),
        KnimeParameter("TZI EnabledStatus", XSD.boolean, True, 'EnabledStatus',
                       path="model/dateTimeFormats/timezone_Internals"),
        KnimeParameter("Auto Range Axes", XSD.boolean, True, 'autoRange', path="model"),
        KnimeParameter("Use Domain Information", XSD.boolean, False, 'useDomainInformation', path="model"),
        KnimeParameter("Always Show Origin", XSD.boolean, False, 'enforceOrigin', path="model"),
        KnimeParameter("Show Selected Only", XSD.boolean, False, 'showSelectedOnly', path="model"),
        KnimeParameter("Chart Title", XSD.string, "", 'chartTitle', path="model"), 
        KnimeParameter("Chart Subtitle", XSD.string, "", 'chartSubtitle', path="model"),
        KnimeParameter("Show Grid", XSD.boolean, False, 'showGrid', path="model"),
        KnimeParameter("Image Width", XSD.int, 800, 'imageWidth', path="model"),
        KnimeParameter("Image Height", XSD.int, 600, 'imageHeight', path="model"),
        KnimeParameter("Resize to Full Window", XSD.boolean, True, 'resizeToWindow', path="model"),
        KnimeParameter("Display Full Screen Button", XSD.boolean, True, 'displayFullscreenButton', path="model"),
        KnimeParameter("Background Color", XSD.string, "rgba(255,255,255,1.0)", 'backgroundColor', path="model"),
        KnimeParameter("Data Area Color", XSD.string, "rgba(255,255,255,1.0)", 'dataAreaColor', path="model"),
        KnimeParameter("Grid Color", XSD.string, "rgba(230,230,230,1.0)", 'gridColor', path="model"),
        KnimeParameter("Show Warning In View", XSD.boolean, True, 'showWarningInView', path="model"),
        KnimeParameter("Enable View Configuration", XSD.boolean, True, 'enableViewConfiguration', path="model"),
        KnimeParameter("Enable Title Change", XSD.boolean, True, 'enableTitleChange', path="model"),
        KnimeParameter("Enable Subtitle Change", XSD.boolean, True, 'enableSubtitleChange', path="model"),
        KnimeParameter("Enable X Column Change", XSD.boolean, True, 'enableXColumnChange', path="model"),
        KnimeParameter("Enable Y Column Change", XSD.boolean, True, 'enableYColumnChange', path="model"),
        KnimeParameter("Enable X Axis Label Edit", XSD.boolean, True, 'enableXAxisLabelEdit', path="model"),
        KnimeParameter("Enable Y Axis Label Edit", XSD.boolean, True, 'enableYAxisLabelEdit', path="model"),
        KnimeParameter("Enable Dot Size Change", XSD.boolean, False, 'enableDotSizeChange', path="model"),
        KnimeParameter("Enable Switch Legend", XSD.boolean, False, 'enableSwitchLegend', path="model"),
        KnimeParameter("Enable Mouse Crosshairs", XSD.boolean, False, 'showCrosshair', path="model"),
        KnimeParameter("Snap to Data Points", XSD.boolean, False, 'snapToPoints', path="model"),
        KnimeParameter("Enable Selection", XSD.boolean, True, 'enableSelection', path="model"),
        KnimeParameter("Enable Rectangular Selection", XSD.boolean, True, 'enableRectangleSelection', path="model"),
        KnimeParameter("Enable Lasso Selection", XSD.boolean, False, 'enableLassoSelection', path="model"),
        KnimeParameter("Publish Selection", XSD.boolean, True, 'publishSelection', path="model"),
        KnimeParameter("Subscribe Selection", XSD.boolean, True, 'subscribeSelection', path="model"),
        KnimeParameter("Enable Show Selected Only", XSD.boolean, True, 'enableShowSelectedOnly', path="model"),
        KnimeParameter("Subscribe Filter", XSD.boolean, True, 'subscribeFilter', path="model"),
        KnimeParameter("Enable Panning", XSD.boolean, True, 'enablePanning', path="model"),
        KnimeParameter("Enable Zooming", XSD.boolean, True, 'enableZooming', path="model"),
        KnimeParameter("Enable Drag Zooming", XSD.boolean, False, 'enableDragZooming', path="model"),
        KnimeParameter("Show Zoom Reset Button", XSD.boolean, False, 'showZoomResetButton', path="model"),
        KnimeParameter("hideInWizard", XSD.boolean, False, 'hideInWizard', path="model"),
        KnimeParameter("showLegend", XSD.boolean, False, 'showLegend', path="model"),

    ],
    input = [
        [cb.NormalizedTabularDatasetShape, cb.TabularDataset] 
    ],
    output = [
        cb.ScatterPlotVisualizationShape,
        cb.TabularDatasetShape
    ],
    implementation_type = tb.VisualizerImplementation,
    knime_node_factory = 'org.knime.js.base.node.viz.plotter.scatterSelectionAppender.ScatterPlotNodeFactory',
    knime_bundle = KnimeJSBundle,
    knime_feature = KnimeJSViewsFeature,

)


scatterplot_visualizer_component = Component(
    name = "Scatter Plot Visualizer",
    implementation = scatterplot_visualizer_implementation,
    exposed_parameters=[
        next((param for param in scatterplot_visualizer_implementation.parameters.keys() if param.knime_key == 'xCol'), None), 
        next((param for param in scatterplot_visualizer_implementation.parameters.keys() if param.knime_key == 'yCol'), None)
    ],
    transformations = [
        CopyTransformation(1, 2),
        Transformation(
            query = '''
INSERT DATA {
    $output2 dmop:hasColumn _:scatterColumn .
    _:scatterColumn a dmop:Column ;
                    dmop:hasName "Selected (Scatter Plot)" ;
                    dmop:hasValue false .
}
'''
        )
    ]
)
