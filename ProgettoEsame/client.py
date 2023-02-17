########### LIBRERIE ###########

import cv2
from simple_facerec import SimpleFacerec
import datetime
from secret import secret
import os
from requests import post


########### URL DEL SERVER DI GCP ###########

base_url = 'https://progettoesame-378100.appspot.com/'


########### UTILIZZO MODULO SIMPLEFACEREC IMPORTATO DA SIMPLE_FACEREC.PY ###########

sfr = SimpleFacerec()
sfr.load_encoding_images("images/")


########### FUNZIONAMENTO DEL VIDEOCITOFONO ###########

old_name = []
current_name = []
name_images = []

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    face_locations, face_names = sfr.detect_known_faces(frame)
    date = datetime.datetime.now()
    h = date.time().strftime("%H:%M:%S")
    cv2.putText(frame, h, (10, 50), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)


    ########### RILEVAMENTO VOLTI E IDENTIFICAZIONE ###########

    for face_loc, name in zip(face_locations, face_names):
        y1, x2, y2, x1 = face_loc[0], face_loc[1], face_loc[2], face_loc[3]
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 4)
        cv2.rectangle(frame, (x2, y1 -30), (x1, y1), (0, 255, 0), cv2.FILLED)
        cv2.putText(frame, name, (x1,y1-10), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 255), 1)


        ########### INVIO INFORMAZIONI PREMENDO IL CAMPANELLO ###########

        if cv2.waitKey(1) & 0xFF == ord('s'):
            name_image = f'{h}_{name}.png'
            cv2.imwrite(name_image, frame)
            files = {'file': open(name_image, 'rb')}
            r = post(f'{base_url}/sensors/cam', data={'name': name, 'time': h, 'secret': secret}, files=files)
            name_images.append(name_image)

        current_name = face_names

    cv2.imshow("Videocitofono", frame)


    if old_name != current_name:
        old_name = current_name
        print('This is ', name,' at ', h)


    ########### SPEGNIMENTO VIDEOCITOFONO ###########

    if cv2.waitKey(1) & 0xFF == 27:
        for name in name_images:
            os.remove(name)
        break


cap.release()
cv2.destroyAllWindows()