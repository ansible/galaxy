import { NgModule } from '@angular/core';

import {
    RouterModule,
    Routes
} from '@angular/router';

import { SearchComponent } from './search.component';

import {
    PopularCloudPlatformsResolver,
    PopularPlatformsResolver,
    PopularTagsResolver,
    SearchCloudPlatformResolver,
    SearchContentResolver,
    SearchContentTypeResolver,
    SearchPlatformResolver
}  from './search.resolver.service';

const routes: Routes = [
    {
        path: '',
        component: SearchComponent,
        runGuardsAndResolvers: 'always',
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
