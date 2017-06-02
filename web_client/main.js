import events from 'girder/events';
import router from 'girder/router';

import ItemView from 'girder/views/body/ItemView';
import { wrap } from 'girder/utilities/PluginUtils';
import itemMenuModTemplate from './templates/itemMenu.pug';
wrap(ItemView, 'render', function (render) {
    this.once('g:rendered', function () {
        const path = (this.model.get('meta') || {}).versionedFilePath;
        if (path) {
            this.$('.g-item-actions-menu').prepend(itemMenuModTemplate({
                path
            }));
        }
    }, this);
    return render.call(this);
});

import DataRevisionsView from './views/DataRevisionsView.js';
router.route('data_revision_history', 'dataRevisions', function (params) {
    events.trigger('g:navigateTo', DataRevisionsView, {
        path: params.path
    });
});
