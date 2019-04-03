import { Component, Input, OnInit } from '@angular/core';

import { CardConfig } from 'patternfly-ng/card/basic-card/card-config';
import { RepoFormats } from '../../../enums/repo-types.enum';
import { Content } from '../../../resources/content/content';
import { Repository } from '../../../resources/repositories/repository';
import { CollectionDetail } from '../../../resources/collections/collection';

class InfoData {
    tags: string[];
    latest_version: string;
    versions: string[];
    last_commit: string;
    last_import: string;
    apb_metadata: string;
    install_cmd: string;
    min_ansible_version: any;
}

@Component({
    selector: 'card-info',
    templateUrl: './card-info.component.html',
    styleUrls: ['./card-info.component.less'],
})
export class CardInfoComponent implements OnInit {
    // Used to track which component is being loaded
    componentName = 'CardInfoComponent';

    constructor() {}
    @Input()
    set repository(repo: Repository) {
        if (repo) {
            this.infoData.last_commit = repo.last_commit;
            this.infoData.last_import = repo.last_import;
        }
    }

    @Input()
    repoType?: RepoFormats;

    @Input()
    set metadata(metadata) {
        this.infoData.apb_metadata = metadata;
    }

    // We're using setter functions here so that the data passed to the
    // component is bound directly to our infoData object, which has to
    // represent collections and repositories
    @Input()
    set repoContent(repoContent: Content) {
        if (repoContent) {
            let cmd;
            if (this.repoType === 'multi') {
                cmd =
                    `mazer install ${
                        repoContent.summary_fields['namespace']['name']
                    }.` + `${repoContent.summary_fields['repository']['name']}`;
            } else {
                cmd =
                    `ansible-galaxy install ${
                        repoContent.summary_fields['namespace']['name']
                    }.` + `${repoContent.name}`;
            }

            this.infoData.install_cmd = cmd;
            this.infoData.tags = repoContent.summary_fields['tags'];
            this.infoData.min_ansible_version = repoContent.min_ansible_version;
        }
    }

    @Input()
    set collection(collection: CollectionDetail) {
        this.infoData = {
            install_cmd: `mazer install ${collection.namespace.name}.${
                collection.name
            }`,
            tags: collection.latest_version.metadata.tags,
            latest_version: `${collection.latest_version.version} uploaded ${
                collection.latest_version.created
            }`,
        } as InfoData;
    }

    config: CardConfig;

    infoData = {
        tags: null,
        latest_version: null,
        versions: null,
        last_commit: null,
        last_import: null,
        apb_metadata: null,
        install_cmd: null,
        min_ansible_version: null,
    } as InfoData;

    ngOnInit() {
        this.config = {
            title: 'Info',
            titleBorder: true,
            topBorder: true,
        } as CardConfig;
    }

    private mapRepository() {}
}
