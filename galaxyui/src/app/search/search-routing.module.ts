import { NgModule } from '@angular/core';

import {
	Routes,
	RouterModule
} from '@angular/router';

import { SearchComponent } from './search.component';

import {
	SearchCloudPlatformResolver,
	SearchContentResolver,
	SearchContentTypeResolver,
	SearchPlatformResolver,
	PopularTagsResolver,
	PopularPlatformsResolver,
	PopularCloudPlatformsResolver
}  from './search.resolver.service';

const routes: Routes = [
	{
		path: 'search',
		component: SearchComponent,
		resolve: {
			cloudPlatforms: SearchCloudPlatformResolver,
			content: SearchContentResolver,
			contentTypes: SearchContentTypeResolver,
			platforms: SearchPlatformResolver,
			popularTags: PopularTagsResolver,
			popularCloudPlatforms: PopularCloudPlatformsResolver,
			popularPlatforms: PopularPlatformsResolver
		},
	}
];

@NgModule({
    imports: [
    	RouterModule.forChild(routes)
    ],
    exports: [
  	    RouterModule
  	],
  	providers: [
  		SearchCloudPlatformResolver,
		SearchContentResolver,
		SearchContentTypeResolver,
		SearchPlatformResolver,
		PopularTagsResolver,
		PopularPlatformsResolver,
		PopularCloudPlatformsResolver
  	]
})
export class SearchRoutingModule { }
