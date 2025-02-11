# FILE MANAGMENT MODULE

#Standard library imports
import os
import shutil
import sys
import pandas as pd

# Local modules
from utils import security


@validate_filenames()
def create_dir(folder_path):
    # 1) Verifica si el directorio existe y confirma si es necesario vaciarlo
    if os.path.exists(folder_path):
        print(f"🚨 ALERTA: El directorio en el que quieres guardar ya tiene contenido, para proceder deberás eliminarlo.")
        confirmation = input(f"❓¿Estás seguro de que deseas eliminar el directorio '{folder_path}' y su contenido? (y/n): ").lower()
        if confirmation in ['y', 'yes']:
            shutil.rmtree(folder_path)  # Elimina el directorio y todo su contenido
            print("> Directorio eliminado:\n",folder_path)
        else:
            print(f"❌ Operación cancelada por el usuario. El directorio no se eliminó.\n⏸️ La ejecución se ha detenido.")
            sys.exit()
    else:
        print("🆕 El directorio no existe, se creará uno nuevo:",{folder_path})
        
    # 2) Crea el directorio especificado
    os.makedirs(folder_path, exist_ok=True)
    print("✅ El directorio ya está disponible:\n",{folder_path})


@validate_filenames()
def empty_dir(folder_path):
    """
    Elimina todo el contenido (archivos y subdirectorios) de una carpeta especificada.

    Args:
        folder_path: La ruta de la carpeta que se va a limpiar.

    Raises:
        FileNotFoundError: Si la carpeta especificada no existe.
        OSError: Si ocurre un error durante la eliminación de archivos o directorios.
    """

    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"❗️La carpeta '{folder_path}' no existe.")

    try:
        confirmation = input(f"❓¿Estás seguro de que deseas eliminar el contenido de '{folder_path}'? (y/n): ").lower()
        if confirmation in ['y', 'yes']:
            for file in os.listdir(folder_path):  # Itera sobre los archivos y directorios
                file_path = os.path.join(folder_path, file)  # Crea la ruta completa

                if os.path.isfile(file_path):  # Si es un archivo
                    os.remove(file_path)  # Elimina el archivo
                    #print(f"Archivo eliminado: {file_path}")

                elif os.path.isdir(file_path):  # Si es un directorio
                    shutil.rmtree(file_path)  # Elimina el directorio y su contenido de forma recursiva
                    #print(f"Directorio eliminado: {file_path}")

            print("✔️ Contenido de la carpeta eliminado:\n", folder_path)

        else:
            print(f"❌ Operación cancelada por el usuario. El directorio no se eliminó.\n⏸️ La ejecución se ha detenido.")
            sys.exit()

    except OSError as e:
        raise OSError(f"🚫 Error al limpiar la carpeta:\n {e}")    
    except FileNotFoundError as e:
        print(f"🚨 El archivo no existe:\n {e}")
    except Exception as e:
        raise Exception(f"❗️ Error inesperado:\n {e}")
    

@validate_filenames()
def build_filename(dset: str, type: str, dir: str='in', prefix: str = '', name: str | None = None, verbose: bool = False) -> str:
    """ 
    Construye el nombre y ruta necesaria para cargar/guardar cada archivo del dataset.

    Parámetros:
        - dset (str): Nombre del subconjunto de datos sobre el que se trabaja ('train', 'valid' o 'test').
        - prefix (str): Establece un prefijo para el archivo.
        - type (str): Tipo de archivo ('image' o 'label').
        - dir (str): Dataset de entrada o de salida ('in' o 'out').
        - name (str, optional): Nombre de archivo (sin extension). Si es None, devuelve la ruta de la carpeta.
        - verbose (bool): Ofrece información verbal al usuario.

    Retorna:
        - str: Por defecto entega la ruta de la carpeta.
        - Si se incluye un nombre de archivo, devuelve la ruta con el formato adecuado.
    """
    assert (isinstance(name, str | None)
            and isinstance(dset, str)
            and isinstance(type, str)
            and isinstance(prefix, str)
            and isinstance(dir, str)), "❕All arguments must be strings."
    
    # This help splitting the name in half
    # for inserting the prefix next to photo filename (eg: 209_205_50_JPG)
    pointer = name.find('.rf.') if name != None else "" # could be modified for differente tag name formats

    file_type = ['images', 'labels']
    file_ext = ['jpg', 'txt']
    set_path = ['train/','valid/','test/']
    
    # Example:
    #    - in: "/data/raw/3.5m.v3i.yolov8/valid/labels/
    #            209_205_50_JPG.rf.a6fdbfed5ddcebe949b5a721c39c6a1f.txt"
    #    - out: "/data/processed/3.5m.v3i.yolov8/valid/labels/
    #            tile00x00.209_205_50_JPG.rf.a6fdbfed5ddcebe949b5a721c39c6a1f.txt"
    #    - shape: /data/{dir}/{PATH}/{dset}/{type}/ <- Folder path
    #             {prefix}.{filename}.{type}        <- Full filename

    if dir == 'out':
        root = PATH.replace('raw','processed')
    elif dir == 'in':
        root = PATH
    else:
        raise ValueError("❕Invalid 'dir': must be 'in' (default) or 'out'.")

    match dset.lower():
        case 'train':
            dset = set_path[0]
        case 'valid':
            dset = set_path[1]
        case 'test':
            dset = set_path[2]
        case _:
            raise ValueError("❕Invalid 'dset': must be 'train', 'valid', or 'test'.")

    if type == 'image':
        type_folder = file_type[0]
        extension = file_ext[0]
    elif type == 'label':
        type_folder = file_type[1]
        extension = file_ext[1]
    else:
        raise ValueError("❕Invalid 'type': must be 'image' or 'label'.")
    
    if name == None or '':
        filename = ''
        print("🚨 WARNING: Prefix will be ignored unless a filename is provided.") if prefix else ''
    else:
        if not prefix:
            # If no prefix is defined, it keeps the original name
            filename = f"{name}.{extension}"
        else:
            if pointer == -1:
                # When the reference in name format is not find, it add the prefix at the end
                filename = f"{name}.{prefix}.{extension}"
            else:
                # If the format is ok, it insert the prefix in between the original JPG filename and the hash part
                name_jpg = name[:pointer]
                name_hash = name[pointer:]
                filename = f"{name_jpg}.{prefix}{name_hash}.{extension}"
                
    if verbose:
        print("✔️ Filename created succesfully")

    return f"{root}{dset}{type_folder}/{filename}"


def filenames_for_tiles(dset: str, type: str, dir: str='in', name: str | None = None) -> callable:
    """ 
    Crea una función anidada para generar nombres de archivo y ruta para cada mosaico.

    Parámetros:
        - dset (str): Nombre del subconjunto de datos sobre el que se trabaja ('train', 'valid' o 'test').
        - type (str): Tipo de archivo ('image' o 'label').
        - dir (str): Dataset de entrada o de salida ('in' o 'out').
        - name (str, optional): Nombre de archivo (sin extension). Si es None, devuelve la ruta de la carpeta.

    Retorna:
        - callable: Retorna la función generadora anidada.
    """
    def generate_filename(prefix: str = '') -> str:
        """
        Construye el nombre y ruta para el mosaico especificado.
        """
        return build_filename(dset=dset, type=type, dir=dir, prefix=prefix, name=name, verbose=False)

    return generate_filename  # Return the nested function


@validate_filenames()
def save_labels(dest_labels_file: str, export: pd.DataFrame, verbose: bool = True) -> bool:
    """
    Saves a DataFrame to a file, with each row as a space-separated string.

    Args:
        dest_labels_file: Path to the output file.
        export: DataFrame to save.

    Returns:
        True if the file was saved successfully, False otherwise.
    """
    try:
        lines = label_to_str(export)
        with open(dest_labels_file, 'w') as file:
            file.writelines(line + "\n" for line in lines)
        if verbose:
            print("El archivo de etiquetas se ha creado correctamente. Se han guardado todos los datos.")
        return True
    
    except OSError as e:
        raise OSError(f"🚫 Error al copiar la carpeta:\n {e}")
    except FileNotFoundError as e:
        print(f"🚨 El archivo no existe:\n {e}")
    except Exception as e:
        raise Exception(f"❗️ Error inesperado:\n {e}")