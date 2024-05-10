class Task:
    def __init__(self, socket_id: str, qr_content: str, init_image: str, 
                 prompt: str, guidance_scale: int, controlnet_conditioning_scale: float, 
                 strength: float):
        self.qr_content = qr_content
        self.socket_id = socket_id
        self.init_image = init_image
        self.prompt = prompt
        self.guidance_scale = guidance_scale
        self.controlnet_conditioning_scale = controlnet_conditioning_scale
        self.strength = strength

    def to_json(self):
        return {
            "socket_id": self.socket_id,
            "qr_content": self.qr_content,
            "prompt": self.prompt,
            "guidance_scale": self.guidance_scale,
            "controlnet_conditioning_scale": self.controlnet_conditioning_scale,
            "strength": self.strength,
            "init_image": self.init_image
        }

    def from_json(json):
        return Task(
            socket_id=json["socket_id"],
            qr_content=json["qr_content"],
            prompt=json["prompt"],
            guidance_scale=json["guidance_scale"],
            controlnet_conditioning_scale=json["controlnet_conditioning_scale"],
            strength=json["strength"],
            init_image=json["init_image"]
        )


class Result:
    def __init__(self, socket_id: str, image: str):
        self.socket_id = socket_id
        self.image = image

    def to_json(self):
        return {
            "socket_id": self.socket_id,
            "image": self.image
        }

    def from_json(json):
        return Result(
            socket_id=json["socket_id"],
            image=json["image"]
        )
