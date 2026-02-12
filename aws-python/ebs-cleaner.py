import boto3
import logging
import sys
from botocore.exceptions import ClientError

# 1. Configuración de Logging (Estándar SRE para observabilidad)
logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}'
)
logger = logging.getLogger(__name__)

def get_unused_volumes(ec2_client):
    """Identifica volúmenes que no están atados a ninguna instancia."""
    try:
        volumes = ec2_client.describe_volumes(
            Filters=[{'Name': 'status', 'Values': ['available']}]
        )
        return volumes.get('Volumes', [])
    except ClientError as e:
        logger.error(f"Error al describir volúmenes: {e}")
        return []

def delete_volume(ec2_client, volume_id, dry_run=True):
    """Elimina un volumen específico. Usa dry_run para pruebas seguras."""
    try:
        if dry_run:
            logger.info(f"[DRY RUN] Volumen {volume_id} sería eliminado.")
            return
        
        ec2_client.delete_volume(VolumeId=volume_id)
        logger.info(f"Volumen {volume_id} eliminado exitosamente.")
    except ClientError as e:
        logger.error(f"No se pudo eliminar el volumen {volume_id}: {e}")

def main():
    # 2. Inicialización del cliente con manejo de sesión
    session = boto3.Session()
    ec2 = session.client('ec2', region_name='us-east-1')

    # 3. Lógica principal
    unused_volumes = get_unused_volumes(ec2)
    
    if not unused_volumes:
        logger.info("No se encontraron volúmenes huérfanos.")
        sys.exit(0)

    for vol in unused_volumes:
        vol_id = vol['VolumeId']
        # 4. Control de seguridad: Siempre empezar con dry_run=True
        delete_volume(ec2, vol_id, dry_run=True)

if __name__ == "__main__":
    main()