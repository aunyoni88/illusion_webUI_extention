from fastapi import FastAPI, Body

from modules.api.models import *
from modules.api import api
import gradio as gr
from datetime import datetime, timezone
import time

from app import inference
from main import decode_base64_to_image, encode_pil_to_base64


def illusion_remove_api(_: gr.Blocks, app: FastAPI):
    @app.post('/sdapi/ai/v1/arif_illusion')
    async def generate_illusion_image(
            input_image: str = Body("", title='illusion input image'),
            prompt: str = Body("", title='prompt'),
    ):
        if not input_image:
            return {
                "success": False,
                "message": "Input image not found",
                "server_hit_time": '',
                "server_process_time": '',
                "output_image": ''
            }
        utc_time = datetime.now(timezone.utc)
        start_time = time.time()
        input_image = decode_base64_to_image(input_image)
        image = inference(
            control_image=input_image,
            controlnet_conditioning_scale=1.2,  # illusion strength
            prompt=prompt if prompt else "landscape of a forest, bright sky, vibrant colors",
            negative_prompt='low quality',
            guidance_scale=7.5,
            sampler="Euler",  # Model or sampler "DPM++ Karras SDE"
            control_guidance_start=0,
            control_guidance_end=1.0,
            upscaler_strength=1.0,
            seed=-1,

        )

        output_image = encode_pil_to_base64(image[0]).decode("utf-8")

        print("time taken: {0}".format(time.time() - start_time))

        return {
            "success": True,
            "message": "Returned output successfully",
            "server_hit_time": str(utc_time),
            "server_process_time": time.time() - start_time,
            "output_image": output_image
        }


try:
    import modules.script_callbacks as script_callbacks

    script_callbacks.on_app_started(illusion_remove_api)

except:
    pass
