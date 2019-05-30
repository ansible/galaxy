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

    // Used on the search page to override the list of contents show with the
    // list of matched items.
    @Input()
    matchList?: any;

    contentTypes: string[];
    maxContent = 3;
    expanded = false;
    canExpand = false;
    contentSummary: any;

    constructor() {}

    ngOnInit() {
        // If the matchList arg is provided to the component, use that as the
        // list of contents to display. Otherwise, use the list of all contents
        // If match list is undefined that means that the parameter hasn't been
        // set. It can still be set but still be null.
        if (this.matchList !== undefined) {
            this.contentSummary = this.matchList;
        } else {
            this.contentSummary = this.collection.latest_version.content_summary;
        }

        if (this.contentSummary) {
            this.contentTypes = Object.keys(this.contentSummary.contents);
            for (const item of this.contentTypes) {
                if (
                    this.contentSummary.contents[item].length > this.maxContent
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
