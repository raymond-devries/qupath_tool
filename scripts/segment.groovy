import org.slf4j.LoggerFactory
import qupath.ext.stardist.StarDist2D
import qupath.lib.images.ImageData
import qupath.lib.images.servers.ColorTransforms
import qupath.lib.images.servers.ImageServers
import qupath.lib.objects.PathObjects
import qupath.lib.roi.ROIs
import qupath.opencv.ml.pixel.PixelClassifierTools

import static qupath.lib.scripting.QP.*

def logger = LoggerFactory.getLogger("segment_logger")

def filePath = args[0]
def testFlag = args[1]
def minNucleiArea = args[2] as int
def threshold = args[3] as double

logger.info('Starting StarDist cell segmentation')
def inputFile = new File("/data/${filePath}")
def server = ImageServers.buildServer(inputFile.toURI().toString())
def imageData = new ImageData(server)
imageData.setImageType(ImageData.ImageType.BRIGHTFIELD_H_DAB)


def classifier = loadPixelClassifier("/scripts/tumor_classifier.json")
def classifierServer = PixelClassifierTools.createPixelClassificationServer(imageData, classifier)
def cellClumps = PixelClassifierTools.createObjectsFromPixelClassifier(classifierServer, null, null, { roi -> PathObjects.createDetectionObject(roi) }, 0.0, 0.0, true)

logger.info("Detected ${cellClumps.size()} cell clumps from pixel classifier")

def pixelSize = server.getPixelCalibration().getAveragedPixelSize()
logger.info("Pixel size from image metadata: ${pixelSize}")

// Extract file stem (filename without extension)
def fileStem = filePath.replaceAll(/\.[^.]+$/, '')
def folderPath = "/data/${fileStem}_segments"
def outputDir = new File(folderPath)
if (!outputDir.exists()) {
    outputDir.mkdirs()
    logger.info("Created output directory: ${outputDir.absolutePath}")
}

def modelPath = "/scripts/models/stardist_model_1_channel.pb"
def stardist_segmentation = StarDist2D
        .builder(modelPath)
        .preprocessGlobal(                 // Apply normalization, calculating values across the whole image
                StarDist2D.imageNormalizationBuilder()
                        .maxDimension(4096)    // Figure out how much to downsample large images to make sure the width & height are <= this value
                        .percentiles(1, 99.8)  // Calculate image percentiles to use for normalization
                        .build()
        )
        .threshold(threshold)              // Prediction threshold
        .includeProbability(true)    // Include prediction probability as measurement
        .pixelSize(0.5)              // Resolution for detection
        .channels(
                ColorTransforms.createColorDeconvolvedChannel(imageData.getColorDeconvolutionStains(), 1),
                ColorTransforms.createColorDeconvolvedChannel(imageData.getColorDeconvolutionStains(), 2)
        )
        .measureShape()              // Add shape measurements
        .measureIntensity()          // Add cell measurements (in all compartments)
        .build()

// Loop through each cell clump and segment
cellClumps.eachWithIndex { clump, index ->
    logger.info("Processing clump ${index + 1} of ${cellClumps.size()}")

    def clumpROI = clump.getROI()

    // Conditionally create test ROI or use full clump
    def roiToUse
    if (testFlag == 'test') {
        def centerX = clumpROI.getCentroidX()
        def centerY = clumpROI.getCentroidY()
        def radius = 1000.0  // 2000x2000 circle
        roiToUse = ROIs.createEllipseROI(centerX - radius, centerY - radius, radius * 2, radius * 2, clumpROI.getImagePlane())
        logger.info("Test mode: Using 2000x2000 circle ROI centered at (${centerX}, ${centerY})")
    } else {
        roiToUse = clumpROI
        logger.info("Production mode: Using full clump ROI")
    }

    def detected = stardist_segmentation.detectObjects(imageData, roiToUse)

    logger.info("Detected ${detected.size()} cells in clump ${index + 1}")
    detected.removeAll { measurement(it, 'Area µm^2') < minNucleiArea }
    logger.info("After filtering: ${detected.size()} cells remain")

    // Export to GeoJSON file named by clump index
    def geoJsonPath = "${folderPath}/clump_${index}.json"
    exportObjectsToGeoJson(detected, geoJsonPath)
    logger.info("Exported clump ${index + 1} to ${geoJsonPath}")
}

logger.info("Done! Processed ${cellClumps.size()} clumps")
