from PIL import Image
import numpy as np



class Steganography:
    """
    class for embedding and extracting to and from images
    """
    def bytesToBinaryHelper(self, data: bytes) -> str:
        """
        converts bytes to binary string with 32 bit length header
        :param data: bytes of data to be converted to binary string
        """
        dataLen = len(data)
        binaryLen = format(dataLen, '032b')
        binaryData = ''.join(format(byte, '08b') for byte in data)
        return binaryLen + binaryData


    def embed(self, inputImagePath: str, data: bytes, outputImagePath: str):
        """
        embeds the given data into the least significant bits (LSBs) of the pixel values of the input image by
        modifying the least significant bits of each color channel (Red, Green, Blue) in each pixel.
        :param inputImagePath: path to the image to be embedded
        :param data: data to be hidden in the image
        :param outputImagePath: path to the output image
        """
        img = Image.open(inputImagePath).convert("RGB")
        pixels = np.array(img)

        binaryData = self.bytesToBinaryHelper(data)

        if len(binaryData) > pixels.size * 3:
            raise ValueError("Data too large for image capacity")

        # embed bits into LSB
        dataIndex = 0
        for row in range(img.height):
            for col in range(img.width):
                for channel in range(3):
                    if dataIndex < len(binaryData):
                        pixels[row, col, channel] = (pixels[row, col, channel] & 254) | int(binaryData[dataIndex])
                        dataIndex += 1

        Image.fromarray(pixels).save(outputImagePath)
        print(f"Embedded {len(data)} bytes into {outputImagePath}")

    def binaryToBytesHelper(self, binaryString: str) -> bytes:
        """
        converts binary string to bytes
        :param binaryString: binary string to be converted to bytes
        :return: converted bytes
        """
        paddedString = binaryString.ljust((len(binaryString) + 7) // 8 * 8, '0')
        return bytes(int(paddedString[i:i + 8], 2) for i in range(0, len(paddedString), 8))

    def extract(self, steganographicImagePath: str) -> bytes:
        """
        extracts hidden data from the steganographic image
        :param steganographicImagePath:
        :return:
        """
        img = Image.open(steganographicImagePath).convert("RGB")
        pixels = np.array(img)

        binaryString = ''.join(str(pixels[row, col, channel] & 1)
                               for row in range(img.height)
                               for col in range(img.width)
                               for channel in range(3))

        dataLen = int(binaryString[:32], 2)
        dataBits = binaryString[32: 32 + (dataLen * 8)]

        return self.binaryToBytesHelper(dataBits)