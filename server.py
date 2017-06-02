import json
from girder import constants, events
from girder.api import access
from girder.api.describe import Description, autoDescribeRoute
from girder.api.rest import boundHandler, filtermodel
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


@access.public(scope=constants.TokenScope.DATA_READ)
@boundHandler()
@filtermodel('item')
@autoDescribeRoute(
    Description('Retrieve a list of ')
    .param('path', 'Canonical path of the versioned file.')
    .pagingParams(
        defaultSort='meta.versionedFileRevision', defaultSortDir=constants.SortDir.DESCENDING)
)
def _getRevisionsByPath(self, path, limit, offset, sort, params):
    cursor = self.model('item').find({
        'meta.versionedFilePath': {'$eq': path}
    }, sort=sort)
    return list(self.model('item').filterResultsByPermission(
        cursor=cursor, user=self.getCurrentUser(), level=constants.AccessType.READ, limit=limit,
        offset=offset))


def load(info):
    events.bind('model.file.finalizeUpload.after', info['name'], _handleRevisionUpload)

    ModelImporter.model('item').ensureIndex(([
         ('meta.versionedFilePath', constants.SortDir.ASCENDING),
         ('meta.versionedFileRevision', constants.SortDir.DESCENDING)
    ], {}))

    info['apiRoot'].item.route('GET', ('data_revisions',), _getRevisionsByPath)
