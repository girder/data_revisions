import json
from girder import constants, events
from girder.utility.model_importer import ModelImporter


def _handleRevisionUpload(event):
    upload = event.info['upload']

    ref = upload.get('reference')

    try:
        ref = json.loads(ref)
    except (TypeError, ValueError):
        return

    if not isinstance(ref, dict):
        return

    path = ref.get('versionedFilePath')
    if path:
        file = event.info['file']
        itemModel = ModelImporter.model('item')
        item = itemModel.load(file['itemId'], force=True)

        maxRev = itemModel.find({
            'meta.versionedFilePath': path,
        }, fields={
            'meta.versionedFileRevision': True
        }, sort=[('meta.versionedFileRevision', constants.SortDir.DESCENDING)], limit=1)

        if maxRev.count() == 0:
            revision = 1
        else:
            revision = maxRev.next()['meta']['versionedFileRevision'] + 1

        itemModel.update({'_id': item['_id']}, update={
            '$set': {
                'meta.versionedFilePath': path,
                'meta.versionedFileRevision': revision
            }
        }, multi=False)


def load(info):
    events.bind('model.file.finalizeUpload.after', info['name'], _handleRevisionUpload)

    ModelImporter.model('item').ensureIndex(([
         ('meta.versionedFilePath', constants.SortDir.ASCENDING),
         ('meta.versionedFileRevision', constants.SortDir.DESCENDING)
    ], {}))
