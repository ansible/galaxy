import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { CollectionDetail } from '../../resources/collections/collection';

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

    constructor(private route: ActivatedRoute, private router: Router) {}

    ngOnInit() {
        this.route.data.subscribe(data => {
            console.log(data.collection);
            if (data.collection['name']) {
                this.collection = data.collection;
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
            } else {
                this.router.navigate(['not-found']);
            }
        });
    }
}
