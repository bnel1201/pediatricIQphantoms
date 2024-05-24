# %%
import os 
from pathlib import Path
from argparse import ArgumentParser

import tensorflow as tf
import SimpleITK as sitk

dir_path = Path(os.path.dirname(os.path.realpath(__file__)))

def denoise(input_dir, output_dir=None, model=None, batch_size=10):
    output_dir = output_dir or (str(input_dir) + '_denoised')
    model = model or (dir_path / 'simple_cnn_denoiser')
    denoiser = tf.keras.models.load_model(model)

    for series in Path(input_dir).rglob('*.mhd'):
        if series.stem.startswith('true'):
            continue
        input_image = sitk.ReadImage(series)
        output = Path(str(series).replace(input_dir, output_dir))

        output.parent.mkdir(parents=True, exist_ok=True)
        z, x, y, z = input_image.GetWidth(), input_image.GetHeight(), input_image.GetDepth()
        input_array = sitk.GetArrayViewFromImage(input_image).reshape(z, x, y, 1).astype('float32')
        sp_denoised = denoiser.predict(input_array, batch_size=batch_size)

        sitk.WriteImage(sitk.GetImageFromArray(sp_denoised), output)
        print(f'Saving --> {output}')


if __name__ == '__main__':
    parser = ArgumentParser(description='Runs XCIST CT simulations on XCAT datasets')
    parser.add_argument('input_dir', type=str, default="", help='directory containing images to be processed')
    parser.add_argument('--output_dir', '-o', type=str, default="", help='directory containing images to be processed')
    parser.add_argument('--model', '-m', type=str, default=None, help='directory containing images to be processed')
    args = parser.parse_args()

    denoise(args.input_dir, args.output_dir, args.model)
# %%
