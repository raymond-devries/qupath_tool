import org.slf4j.LoggerFactory
import qupath.ext.stardist.StarDist2D
import qupath.lib.color.ColorDeconvolutionStains
import qupath.lib.images.ImageData
import qupath.lib.images.servers.ColorTransforms
import qupath.lib.roi.RectangleROI

import static qupath.lib.scripting.QP.createFullImageAnnotation
import static qupath.lib.scripting.QP.exportObjectsToGeoJson
import static qupath.lib.scripting.QP.measurement

def logger = LoggerFactory.getLogger("segment_logger")

logger.info('Starting StarDist cell segmentation')
def inputFile = new File("/data/${args[0]}")
def server = new qupath.lib.images.servers.bioformats.BioFormatsServerBuilder().buildServer(inputFile.toURI())
def imageData = new ImageData(server)
imageData.setImageType(ImageData.ImageType.BRIGHTFIELD_H_DAB)
imageData.setColorDeconvolutionStains(ColorDeconvolutionStains.parseColorDeconvolutionStainsArg(
        '{"Name" : "H-DAB default", "Stain 1" : "Hematoxylin", "Values 1" : "0.65111 0.70119 0.29049", "Stain 2" : "DAB", "Values 2" : "0.26917 0.56824 0.77759", "Background" : " 255 255 255"}'
))

def pixelSize = server.getPixelCalibration().getAveragedPixelSize()

logger.info("Pixel size from image metadata: ${pixelSize}")

min_nuclei_area = 10

def modelPath = "/scripts/models/stardist_model_1_channel.pb"
def stardist_segmentation = StarDist2D
        .builder(modelPath)
        .preprocessGlobal(                 // Apply normalization, calculating values across the whole image
                StarDist2D.imageNormalizationBuilder()
                        .maxDimension(4096)    // Figure out how much to downsample large images to make sure the width & height are <= this value
                        .percentiles(1, 99.8)  // Calculate image percentiles to use for normalization
                        .build()
        )
        .threshold(0.2)              // Prediction threshold
        .includeProbability(true)    // Include prediction probability as measurement
        .pixelSize(0.5)              // Resolution for detection
        .channels(
                ColorTransforms.createColorDeconvolvedChannel(imageData.getColorDeconvolutionStains(), 1),
                ColorTransforms.createColorDeconvolvedChannel(imageData.getColorDeconvolutionStains(), 2)
        )
        .channels(1)
        .measureShape()              // Add shape measurements
        .measureIntensity()          // Add cell measurements (in all compartments)
        .build()

def isTest = (args.size() > 1 && args[1] == 'test')

if (isTest) {
    logger.info("Running test")
} else {
    logger.info("Running whole image")
}

def roi = isTest ?
        new RectangleROI(20000, 20000, 100, 100) :
        createFullImageAnnotation(imageData, true).getROI()

def detected = stardist_segmentation.detectObjects(imageData, roi)


logger.info("Detected ${detected.size()} objects.")
detected.removeAll { measurement(it, 'Area µm^2') < min_nuclei_area }

logger.info("Exporting cell shapes to geo json")

def geoJsonPath = "/data/${args[0]}.json"
exportObjectsToGeoJson(detected, geoJsonPath)

logger.info("Done!")
