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
            'meta.versionInfo.path': path,
        }, fields={
            'meta.versionInfo.revision': True
        }, sort={
            'meta.versionInfo.revision': constants.SortDir.DESCENDING
        }, limit=1)

        if maxRev.count() == 0:
            revision = 1
        else:
            revision = maxRev.next()['meta']['versionInfo']['revision'] + 1

        itemModel.update({'_id': item['_id']}, update={
            '$set': {
                'meta.versionInfo': {
                    'path': path,
                    'revision': revision
                }
            }
        }, multi=False)


def load(info):
    events.bind('model.file.finalizeUpload.after', info['name'], _handleRevisionUpload)

    ModelImporter.model('item').ensureIndex(([
         ('meta.versionInfo.path', constants.SortDir.ASCENDING),
         ('meta.versionInfo.revision', constants.SortDir.DESCENDING)
    ], {}))
