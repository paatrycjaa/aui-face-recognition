# aui-face-recognition

Application for face recognition on video streaming

### Architecture
![aui-architecture](https://user-images.githubusercontent.com/44137780/127741211-05409bbc-465d-419f-9bb7-fb10a7657edc.png)


### Face detection
```
cd analyzing_module
python3 -m venv /venv   (python 3.8.5 working)
source venv/bin/activate
pip install tensorflow
pip install mtcnn
pip install git+https://github.com/rcmalli/keras-vggface.git
pip install keras-applications
```
If problem : module 'tensorflow.python.keras.utils.generic_utils' has no attribute 'populate_dict_with_module_objects'
```
pip uninstall tf-nightly
pip install tensorflow --upgrade --force-reinstall
```
### Run
```
python3 facedetection.py
```
