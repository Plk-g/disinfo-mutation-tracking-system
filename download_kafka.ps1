$KAFKA_VERSION = "3.6.0"
$SCALA_VERSION = "2.12"

mkdir tools -Force
cd tools

Invoke-WebRequest `
  -Uri "https://archive.apache.org/dist/kafka/$KAFKA_VERSION/kafka_$SCALA_VERSION-$KAFKA_VERSION.tgz" `
  -OutFile "kafka_$SCALA_VERSION-$KAFKA_VERSION.tgz"

tar -xzf "kafka_$SCALA_VERSION-$KAFKA_VERSION.tgz"
