FROM quay.io/galaxy/qupath-headless:0.6.0-1

COPY scripts/prefs.groovy /scripts/prefs.groovy
RUN /opt/qupath/QuPath/bin/QuPath script /scripts/prefs.groovy

COPY scripts/segment.groovy /scripts/segment.groovy
COPY scripts/models/stardist_model_1_channel.pb /scripts/models/stardist_model_1_channel.pb

ENTRYPOINT ["/opt/qupath/QuPath/bin/QuPath", "script", "/scripts/segment.groovy", "--args"]
