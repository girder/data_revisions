import View from 'girder/views/View';
import ItemCollection from 'girder/collections/ItemCollection';
import PaginateWidget from 'girder/views/widgets/PaginateWidget';
import { SORT_DESC } from 'girder/constants';
import { formatDate, formatSize, DATE_SECOND } from 'girder/misc';
import template from '../templates/itemRevisions.pug';

import 'bootstrap/js/collapse';
import 'bootstrap/js/transition';

const DataRevisionsView = View.extend({
    initialize: function (settings) {
        this.path = settings.path;
        this.items = new ItemCollection();
        this.items.altUrl = `item/data_revisions?path=${this.path}`;
        this.items.sortField = 'meta.versionedFileRevision';
        this.items.sortDir = SORT_DESC;
        this.items.on('g:changed', function () {
            this.render();
        }, this).fetch();

        this.paginateWidget = new PaginateWidget({
            collection: this.items,
            parentView: this
        });
    },

    render: function () {
        this.$el.html(template({
            path: this.path,
            items: this.items.models,
            formatDate,
            formatSize,
            DATE_SECOND
        }));

        this.paginateWidget.setElement(this.$('.g-paginate-container')).render();
    }
});

export default DataRevisionsView;
