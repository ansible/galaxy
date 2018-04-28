import { Component, OnInit } from '@angular/core';
import { Repository } from '../resources/respositories/repository';
import { RepositoryService } from '../resources/respositories/repository.service';
import { ListConfig } from 'patternfly-ng/list/basic-list/list-config';


class TopCard {
  type: string;
  icon: string;
  name: string;
  count: number;
  url: string;

  public constructor(init?:Partial<Person>) {
      Object.assign(this, init);
  }

}

@Component({
  selector: 'app-explore',
  templateUrl: './explore.component.html',
  styleUrls: ['./explore.component.less']
})
export class ExploreComponent implements OnInit {
  headerTitle = 'Explore';
  mostStarredRepos: TopCard[] = [];
  mostWatchedRepos: TopCard[] = [];


  constructor(
    private repositoryService: RepositoryService,
  ) { }

  ngOnInit() {
    this.getMostStarred();
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
        this.mostStarredRepos.push(this.repositoryToTopCard(repositories[0], "Repo", "gear"));
      });
  }
}
