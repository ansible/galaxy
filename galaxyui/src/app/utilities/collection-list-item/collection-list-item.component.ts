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

    @Input()
    expandContent: boolean;

    contentTypes: string[];
    maxContent = 5;
    expanded = false;
    canExpand = false;

    constructor() {}

    ngOnInit() {
        this.contentTypes = Object.keys(
            this.collection.latest_version.content_summary.contents,
        );

        if (this.expandContent) {
            for (const item of this.contentTypes) {
                if (
                    this.collection.latest_version.content_summary.contents[
                        item
                    ].length > this.maxContent
                ) {
                    this.canExpand = true;
                    break;
                }
            }
        }
    }

    formatDate(date) {
        return moment(date).fromNow();
    }

    getSlice(items) {
        if (this.expanded) {
            return items;
        }

        return items.slice(0, this.maxContent);
    }

    toggleExpanded() {
        this.expanded = !this.expanded;
    }
}
