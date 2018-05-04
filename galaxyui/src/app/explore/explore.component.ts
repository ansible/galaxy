import { Component, OnInit } from '@angular/core';
import { Repository } from '../resources/respositories/repository';
import { RepositoryService } from '../resources/respositories/repository.service';
import { ListConfig } from 'patternfly-ng/list/basic-list/list-config';
import { TagsService } from '../resources/tags/tags.service'

class TopCard {
  type: string;
  icon: string;
  name: string;
  count: number;
  url: string;

  // public constructor(init?:Partial<Person>) {
  //     Object.assign(this, init);
  // }

}

@Component({
  selector: 'app-explore',
  templateUrl: './explore.component.html',
  styleUrls: ['./explore.component.less']
})
export class ExploreComponent implements OnInit {
  headerTitle = 'Explore';
  mostStarred: TopCard[] = [];
  mostWatched: TopCard[] = [];
  mostDownloaded: TopCard[] = [];
  topTags: TopCard[] = [];
  topUsers: TopCard[] = [];
  newestItems: TopCard[] = [];

  constructor(
    private repositoryService: RepositoryService,
    private tagsService: TagsService,

  ) { }

  ngOnInit() {
    this.getMostStarred();
    this.getTopTags();
  }

  repositoryToTopCard(repo: Repository, type: string, icon: string): TopCard {
    console.log(repo);
    let card: TopCard ={
      type: type,
      icon: icon,
      name: repo.name,
      count: repo.stargazers_count,
      url: '',
    };

    console.log(card);

    return card;
  }

  getMostStarred(): void {
    this.repositoryService.query({'order_by': '-stargazers_count', 'page_size': '1'})
      .subscribe(repositories => {
        this.mostStarred.push(this.repositoryToTopCard(repositories[0], "Repo", "gear"));
      });
  }

  getTopTags(): void{
    this.tagsService.search({'order_by': '-roles_count', 'page_size': '5'})
      .subscribe(tags => {
        tags.forEach(tag =>{
          this.topTags.push(new TopCard({
            icon: 'tag',
            name: tag.name,
            count: tag.roles_count,
            url: tag.url,
          }))
        });
      });
  }
}
