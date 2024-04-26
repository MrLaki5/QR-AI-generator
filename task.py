from PIL import Image


class Task:
    def __init__(self, socket_id, qr_content: str, init_image: Image, prompt: str, guidance_scale: int, controlnet_conditioning_scale: float, strength: float):
        self.qr_content = qr_content
        self.socket_id = socket_id
        self.init_image = init_image
        self.prompt = prompt
        self.guidance_scale = guidance_scale
        self.controlnet_conditioning_scale = controlnet_conditioning_scale
        self.strength = strength

    def __str__(self):
        return f"Task: {self.socket_id}, {self.qr_content}, {self.prompt}, {self.guidance_scale}, {self.controlnet_conditioning_scale}, {self.strength}"
