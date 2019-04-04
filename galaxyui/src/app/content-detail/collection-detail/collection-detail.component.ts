import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { CollectionDetail } from '../../resources/collections/collection';
import { ViewTypes } from '../../enums/view-types.enum';
import * as moment from 'moment';
import { CommunityDetails, DetailMessage } from '../cards/survey/types';

@Component({
    selector: 'app-collection-detail',
    templateUrl: './collection-detail.component.html',
    styleUrls: ['./collection-detail.component.less'],
})
export class CollectionDetailComponent implements OnInit {
    // Used to track which component is being loaded
    componentName = 'CollectionDetailComponent';
    collection: CollectionDetail;
    pageLoading = true;
    pageTitle: string;
    pageIcon: string;
    ViewTypes: typeof ViewTypes = ViewTypes;
    showingView: string = ViewTypes.detail;
    showQualityDetails = false;
    showComunityDetails = false;
    communityScoreDetails: CommunityDetails[];

    // For binding to the survey
    mappedNamespaceOwners: any[];

    constructor(private route: ActivatedRoute, private router: Router) {}

    ngOnInit() {
        this.route.data.subscribe(data => {
            if (data.collection['name']) {
                this.collection = data.collection;
                this.collection.latest_version.created = moment(
                    this.collection.latest_version.created,
                ).fromNow();
                this.pageLoading = false;

                if (this.collection.namespace.is_vendor) {
                    this.pageTitle = 'Vendors;/vendors;';
                    this.pageIcon = 'fa fa-star';
                } else {
                    this.pageTitle = 'Community Authors;/community;';
                    this.pageIcon = 'fa fa-users';
                }

                // Append author namespace and repository name to breadcrumb
                this.pageTitle += `${this.collection.namespace.name};/${
                    this.collection.namespace.name
                };${this.collection.name};`;

                this.mappedNamespaceOwners = [];
                this.collection.namespace.owners.forEach(id => {
                    this.mappedNamespaceOwners.push({ id: id });
                });
            } else {
                this.router.navigate(['not-found']);
            }
        });
    }

    toggleView(view: string) {
        this.showingView = ViewTypes[view];
    }

    scoreDetailHandler(detailData: DetailMessage) {
        if (detailData.type === 'community') {
            this.communityScoreDetails = detailData.payload;
            this.showComunityDetails = detailData.visible;
        } else if (detailData.type === 'quality') {
            this.showQualityDetails = detailData.visible;
        }
    }

    toggleSurveyDetails(key: string) {
        this[key] = !this[key];
    }

    convertScore(score: number) {
        if (score === null) {
            return 'NA';
        }

        return Math.round(score * 10) / 10;
    }
}
