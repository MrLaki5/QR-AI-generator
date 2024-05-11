import torch
from PIL import Image
from diffusers import StableDiffusionControlNetImg2ImgPipeline, ControlNetModel, DDIMScheduler
import qrcode


def generate_qr_code(content: str, filename: str = None):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(content)
    qr.make(fit=True)
    # Inverted colors seems to work better
    img = qr.make_image(fill_color="white", back_color="black")

    if filename:
        img.save(filename)

    return img


def resize_image(input_image: Image, resolution: int):
    input_image = input_image.convert("RGB")
    W, H = input_image.size
    k = float(resolution) / min(H, W)
    H *= k
    W *= k
    H = int(round(H / 64.0)) * 64
    W = int(round(W / 64.0)) * 64
    img = input_image.resize((W, H), resample=Image.LANCZOS)
    return img


class QRCodeAIGenerator:
    def __init__(self):
        self.controlnet = ControlNetModel.from_pretrained("./qr-ai-models/controlnet_v1p_sd15",
                                                          torch_dtype=torch.float16)

        self.pipe = StableDiffusionControlNetImg2ImgPipeline.from_pretrained(
            "./qr-ai-models/stable_diffusion_v1_5",
            controlnet=self.controlnet,
            torch_dtype=torch.float16
        )
        self.pipe.enable_xformers_memory_efficient_attention()
        self.pipe.scheduler = DDIMScheduler.from_config(self.pipe.scheduler.config)
        self.pipe.enable_model_cpu_offload()

    # guidance_scale: default 20 the higher value (>1) the image will look more like prompt in expense to lower image quality
    # controlnet_conditioning_scale: default 1.5, 0.1 gives results closer to prompt mixed with input image, 2.0 gives results closer to control image
    # strength: default 0.9, 0.1 gives same result as input image, 1.0 gives a more clear QR Code [0.8-1.8]
    def generate_ai_qr_code(self, qr_content: str, init_image: Image, prompt: str, guidance_scale: int = 10,
                            controlnet_conditioning_scale: float = 2.0, strength: float = 1.5):
        # Generate QR Code
        qr_code = generate_qr_code(qr_content)
        
        # Resize images to be same size
        condition_image = resize_image(qr_code, 768)
        initial_image = resize_image(init_image, 768)

        generator = torch.manual_seed(123121231)

        image = self.pipe(prompt=prompt,
            negative_prompt="ugly, disfigured, low quality, blurry, nsfw", 
            image=initial_image,
            control_image=condition_image,
            width=768,
            height=768,
            guidance_scale=guidance_scale,
            controlnet_conditioning_scale=controlnet_conditioning_scale,
            generator=generator,
            strength=strength,
            num_inference_steps=150,
        )
        img = image.images[0]

        return img


if __name__ == "__main__":
    from diffusers.utils import load_image
    import argparse

    # create parser
    parser = argparse.ArgumentParser(description="Generate AI QR Code")
    parser.add_argument("--qr_content", type=str, help="QR Code content")
    parser.add_argument("--prompt", type=str, help="Prompt")
    parser.add_argument("--init_image", type=str, help="Initial image")
    parser.add_argument("--output", type=str, help="Output file")
    parser.add_argument("--guidance_scale", type=int, default=10, help="10, Guidance scale: higher value will make output look more like prompt")
    parser.add_argument("--controlnet_conditioning_scale", type=float, default=2.0, help="2.0, Controlnet conditioning scale: higher value make QR more visible")
    parser.add_argument("--strength", type=float, default=1.5, help="1.5, Strength: higher value will make QR more visible [0.8-1.8]")

    # parse the arguments
    args = parser.parse_args()

    init_image = load_image(args.init_image)
    qr_code_ai_generator = QRCodeAIGenerator()
    ai_qr_code = qr_code_ai_generator.generate_ai_qr_code(args.qr_content, init_image, args.prompt, args.guidance_scale, args.controlnet_conditioning_scale, args.strength)

    ai_qr_code.save(args.output)
