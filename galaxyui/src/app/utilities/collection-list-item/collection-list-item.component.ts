import { Component, OnInit, Input } from '@angular/core';
import { CollectionList } from '../../resources/collections/collection';

import * as moment from 'moment';

@Component({
    selector: 'app-collection-list-item',
    templateUrl: './collection-list-item.component.html',
    styleUrls: ['./collection-list-item.component.less'],
})
export class CollectionListItemComponent implements OnInit {
    // Used to track which component is being loaded
    componentName = 'CollectionListItemComponent';

    @Input()
    collection: CollectionList;

    constructor() {}

    ngOnInit() {}

    formatDate(date) {
        return moment(date).fromNow();
    }
}
