from PIL import Image
import asyncio
import base64
import comfy.utils # pyright: ignore[reportMissingImports]
import io
import json
import numpy as np
import time
import websockets

class SaveImagePixelSocket:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", ),
                "websocket_url": ("STRING", {"default": "ws://localhost:3000"}),
                "file_format": (["WEBM", "PNG", "JPEG"], {"default": "WEBM"}),  # Currently only WEBM is implemented
            }
        }

    RETURN_TYPES = ()
    FUNCTION = "save_images"
    OUTPUT_NODE = True
    CATEGORY = "api/image"

    async def send_to_websocket(self, images, websocket_url, file_format):
        """Send images to WebSocket server"""
        try:
            async with websockets.connect(websocket_url) as websocket:
                pbar = comfy.utils.ProgressBar(images.shape[0])
                for step, image in enumerate(images):
                    # Convert image to NumPy array
                    i = 255. * image.cpu().numpy()
                    img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))

                    # Encode in specified format
                    img_bytes = io.BytesIO()
                    img.save(img_bytes, format=file_format)
                    img_data = img_bytes.getvalue()
                    base64_data = base64.b64encode(img_data).decode('utf-8')

                    # Create JSON metadata
                    metadata = {
                        "type": "image-generated",
                        "data": {
                            "mode": "push",
                            "mimeType": f"image/{file_format.lower()}",
                            "imageInfo": img.info if hasattr(img, 'info') else {},
                            "imageIdx": step,
                            "imageLength": images.shape[0],
                            "timestamp": int(time.time() * 1000),
                            "base64Data": base64_data,
                        }
                    }

                    # Send JSON metadata
                    message = json.dumps(metadata)
                    await websocket.send(message)
                    pbar.update_absolute(step, images.shape[0], f"Sent image {step}")

        except Exception as e:
            print(f"WebSocket send error: {e}")

    def save_images(self, images, websocket_url):
        """Main processing"""
        try:
            asyncio.run(self.send_to_websocket(images, websocket_url, file_format="WEBM"))
        except Exception as e:
            print(f"Error: {e}")

        return {}

    @classmethod
    def IS_CHANGED(cls, images):
        return time.time()

NODE_CLASS_MAPPINGS = {
    "SaveImagePixelSocket": SaveImagePixelSocket,
}
