from transformers import GLPNImageProcessor, GLPNForDepthEstimation
from transformers import DPTImageProcessor, DPTForDepthEstimation
from colorama import Fore, Style
from tkinter import filedialog
from PIL import Image
import numpy as np
import torch
import tqdm
import glob
import time

t1 = time.time()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Select the Directory Yo!")
inImg = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff")])
imgDir = ('/'.join([x.replace(" ", "~") for x in inImg.split("/")[:-1]])).replace("~", " ") + '/'
print("---->", imgDir)
x = [glob.glob(imgDir+y) for y in ['*.jpg', '*.png', '*.tiff', '*.bmp', '*.jpeg']]
x = sum(x, [])
y = [z for z in x if "Depth." not in z]
pbar = tqdm.tqdm(total=len(y), colour="red")
for i in y:
    t1_ = time.time()
    img  = Image.open(i)
    #processor = DPTImageProcessor.from_pretrained("Intel/dpt-hybrid-midas")
    #model = DPTForDepthEstimation.from_pretrained("Intel/dpt-hybrid-midas").to(device)

    processor = GLPNImageProcessor.from_pretrained("vinvino02/glpn-nyu")
    model = GLPNForDepthEstimation.from_pretrained("vinvino02/glpn-nyu").to(device)

    inputs = processor(images=img, return_tensors="pt").to(device)
    with torch.no_grad():
        output = model(**inputs)
        predicted_depth = output.predicted_depth

    prediction = torch.nn.functional.interpolate(
        predicted_depth.unsqueeze(1),
        size = img.size[::-1],
        mode = "bicubic",
        align_corners = False
    )

    print("\n\n\n", prediction)
    output = prediction.squeeze().cpu().numpy()
    print(Fore.BLUE + Style.BRIGHT + "\n\n\n", output)
    out_img = (output * 255 / np.max(output)).astype("uint8")
    print(Fore.MAGENTA + Style.BRIGHT + "\n\n\n", out_img)
    print(Fore.RESET)
    depth = Image.fromarray(out_img)

    z = i.split(".")
    z = str('Depth.').join(z)
    depth.save(z)
    t2_ = time.time()
    print("\n" + Fore.WHITE + Style.BRIGHT + z + " ExecTime:" + str(t2_-t1_) + Fore.RESET)
    pbar.update(1)
t2 = time.time()

pbar.close()
print("\nCompleteExecTime: ", (t2-t1))