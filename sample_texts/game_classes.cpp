#include "game_classes.hpp"
#include <fstream>

int bon_tab[] = {1, 5, 10};
bool change = true;

//wypisywanie obiektu na plansze
void game_object::draw(){
  mvaddch(pl->Y0() + 4 + y, pl->X0() + 1 + x, character | A_BOLD | COLOR_PAIR(color));
}

//konstruktor sciany
wall::wall(playground * Ipl, unsigned int Ix, unsigned int Iy, char Ich, int Icolor){
  pl = Ipl;
  x = Ix;
  y = Iy;
  character = Ich;
  color = Icolor;
  type = wall_t;
}

//konstruktor bonusa
bonus::bonus(playground * Ipl, unsigned int Ix, unsigned int Iy, int points)
  : points(points){
  pl = Ipl;
  x = Ix;
  y = Iy;
  type = bonus_t;

  //rozne znaki i kolory w zaleznosci od punktow
  switch(points){
  case 1:
    character = '%';
    color = 2;
    break;
  case 5:
    character = '@';
    color = 3;
    break;
  case 10:
    character = 'X';
    color = 4;
    break;
  default:
    character = '?';
    color = 2;
    break;
  }
}




//konstruktor kursora
cursor::cursor(playground * Ipl, player * owner, char Ich) : owner(owner) {
  pl = Ipl;
  type = cursor_t;
  character = Ich;
  color = 5;

  x = (pl->Width() - 2) / 2;
  y = (pl->Height() - 5) / 2;
  
  pl->objects[x][y] = this;
}

//destruktor kursora
cursor::~cursor(){
  mvaddch(y, x, ' ');
}

//ruszanie kursora
void cursor::move(direction_t where){
  if(pl->objects[x][y] == this) //warunek zeby przypadkiem nie skasowac czegos innego
    pl->objects[x][y] = NULL;  //kasujemy tam gdzie bylismy

  switch(where){
  case up:
    if(pl->free(x, y-1)) //jesli mozna sie ruszyc
      //wymazujemy stare pole i zmieniamy polozenie
      mvaddch(pl->Y0() + 4 + y--, pl->X0() + 1 + x ,' ');
    break;
  case down:
    if(pl->free(x, y+1))
      mvaddch(pl->Y0() + 4 + y++, pl->X0() + 1 + x ,' ');
    break;
  case left:
    if(pl->free(x-1, y))
      mvaddch(pl->Y0() + 4 + y, pl->X0() + 1 + x-- ,' ');
    break;
  case right:
    if(pl->free(x+1, y))
      mvaddch(pl->Y0() + 4 + y, pl->X0() + 1 + x++ ,' ');
    break;
  }
  draw(); //rysujemy w nowym polozeniu

  if(pl->objects[x][y] == NULL){  //jesli wyladowalismy na niczym
    pl->objects[x][y] = this; //plansza ma wiedziec gdzie jestesmy
    return;
  }
  
  //jesli zjedlismy bonusa
  if(pl->objects[x][y]->Type() == bonus_t){
    owner->add_score( static_cast<bonus*>(pl->objects[x][y])->Points() ); //ja, ja
    delete pl->objects[x][y];
    pl->objects[x][y] = NULL; //juz tam nie ma nic
    pl->add_bonus(); //wrzucamy nowego bonusa na plansze
  }
  pl->objects[x][y] = this; //jak zjedlismy to plansza tez ma wiedziec gdzie jestesmy
}











/////////////
// PLANSZA //
/////////////

//konstruktor planszy
playground::playground(){
  x0 = 0;
  y0 = 0;
  width = COLS;
  height = LINES;

  objects.resize(width-2);
  for(unsigned int i=0; i<objects.size(); i++)
    objects[i].resize(height-5);

  make_null();
  draw();
}

//inny konstruktor
playground::playground(unsigned int width, unsigned int height) : width(width), height(height){
  x0 = (COLS - width) / 2;
  y0 = (LINES - height) / 2;
  objects.resize(width-2);
  for(unsigned int i=0; i<objects.size(); i++)
    objects[i].resize(height-5);

  make_null();
  draw();
}

//destruktor
playground::~playground(){
  make_null();
}


//logiczne czyszczenie planszy
void playground::make_null(){
  for(unsigned int i=0; i<objects.size(); i++){
    for(unsigned int j=0; j<objects[i].size(); j++){
      if(objects[i][j] != NULL && (objects[i][j]->Type() == wall_t || objects[i][j]->type == bonus_t))
	delete objects[i][j];
      objects[i][j] = NULL;
    }
  }
}

//graficzne czyszczenie planszy
void playground::clear(){
  for(unsigned int x = x0+1; x < x0 + width - 1; x++){
    for(unsigned int y = y0+4; y < y0 + height - 1; y++)
      mvaddch(y, x, ' ');
  }
}

//odswiezanie planszy
void playground::refresh(bool clean_first){
  if(clean_first)
    clear(); //najpierw czyscimy

  for(unsigned int i=0; i<objects.size(); i++){
    for(unsigned int j=0; j<objects[i].size(); j++){
      if(objects[i][j] == NULL)
	continue;
      objects[i][j]->draw();
    }
  }

  move(LINES-1, COLS-1); //kursor do rogu ekranu
}

//rysowanie planszy
void playground::draw(){
  //najpierw czyscimy caly ekran
  for(int i=0; i<LINES; i++){
    for(int j=0; j<COLS; j++)
      mvaddch(i,j,' ');
  }

  mvprintw(y0, x0, "Arrow keys to move, 'q' to quit. Spacebar to show AI's plan.");

  move(y0 + 1, x0 + width - 32);
  addch('%' | A_BOLD | COLOR_PAIR(2));
  printw(" - 1 pt, ");
  addch('@' | A_BOLD | COLOR_PAIR(3));
  printw(" - 5 pts, ");
  addch('X' | A_BOLD | COLOR_PAIR(4));
  printw(" - 10 pts");

  //drukujemy ramke dookola
  attron(COLOR_PAIR(1));
  attron(A_BOLD);

  mvaddch(y0+3, x0, '+');
  mvaddch(y0+3, x0+width-1, '+');
  mvaddch(y0+height-1, x0, '+');
  mvaddch(y0+height-1, x0+width-1, '+');
  for(unsigned int x=x0+1; x < x0+width-1; x++)
      mvaddch(y0+3, x, '-');
  for(unsigned int y=y0+4; y < y0+height-1; y++){
    mvaddch(y, x0, '|');
    mvaddch(y, x0+width-1, '|');
  }
  for(unsigned int x=x0+1; x < x0+width-1; x++)
      mvaddch(y0+height-1, x, '-');

  attroff(COLOR_PAIR(1));
  attroff(A_BOLD);
}

//pytanie, czy pole wolne
bool playground::free(int x, int y){
  if(x<0 || y<0 || (unsigned int)x > width-3 || (unsigned int)y > height-6)
    return false;
  if(objects[x][y] == NULL)
    return true;
  if(objects[x][y]->type == wall_t)
     return false;
  return true;
}

//dodawanie sciany
wall * playground::add_wall(unsigned int x, unsigned int y){
  wall * new_wall = new wall(this, x, y, '+', 1);
  objects[x][y] = new_wall;
  objects[x][y]->draw();
  change = true;

  return new_wall;
}

//dodawanie bonusa
bonus * playground::add_bonus(){
  int x, y;
  do{ //losujemy gdzie
    x = rand() % width;
    y = rand() % height;
  } while( !free(x,y) );
  
  
  bonus * new_bonus = new bonus(this, x, y, bon_tab[rand() % 3]);
  objects[x][y] = new_bonus;
  objects[x][y]->draw();

  change = true;

  return new_bonus;
}










///////////
// GRACZ //
///////////

//inicjalizujemy ilosc graczy
int player::count = 0;

//konstruktor
player::player(playground * pl, const char * name, char ch) : score(0), cur(pl, this, ch), pl(pl), name(name) {
  number = count++;

  //drukowanie imienia na gorze
  attron(COLOR_PAIR(1));
  attron(A_BOLD);
  mvprintw(pl->Y0() + 2, pl->X0() + number * 20 + 1, name);
  printw(": ");
  int tmp;
  getyx(stdscr, tmp, score_pos);
  printw("%6i ", score);
  attroff(COLOR_PAIR(1));
  attroff(A_BOLD);

  cur.draw();
}

//dodawanie wyniku
void player::add_score(int n){
  score += n;
  attron(COLOR_PAIR(1));
  attron(A_BOLD);
  mvprintw(pl->Y0() + 2, score_pos, "%6i ", score);
  attroff(COLOR_PAIR(1));
  attroff(A_BOLD);
}










////////
// AI //
////////

//konstruktor
AI::AI(playground * pl, const char * name, player * opponent)
  : me(pl, name, 'C'), opponent(opponent){

  //sposob na alokowanie tablicy wielowymiarowej
  intermediary = new Vertex****[me.pl->Width() - 2];
  for(unsigned int i=0; i < me.pl->Width()-2; i++){
    intermediary[i] = new Vertex***[me.pl->Height() - 5];
    for(unsigned int j=0; j < me.pl->Height() - 5; j++){
      intermediary[i][j] = new Vertex**[me.pl->Width() - 2];
      for(unsigned int k=0; k < me.pl->Width() - 2; k++)
	intermediary[i][j][k] = new Vertex*[me.pl->Height() - 5];
    }
  }

  dist = new int***[me.pl->Width() - 2];
  for(unsigned int i=0; i < me.pl->Width() - 2; i++){
    dist[i] = new int**[me.pl->Height() - 5];
    for(unsigned int j=0; j < me.pl->Height() - 5; j++){
      dist[i][j] = new int*[me.pl->Width() - 2];
      for(unsigned int k=0; k < me.pl->Width() - 2; k++)
	dist[i][j][k] = new int[me.pl->Height() - 5];
    }
  }

  vertices = new Vertex**[me.pl->Width() - 2];
  for(unsigned int i=0; i < me.pl->Width()-2; i++)
    vertices[i] = new Vertex*[me.pl->Height() - 5];

  create_playground_model(); //komputer modeluje sobie plansze
}


//destruktor
AI::~AI(){
  for(unsigned int i=0; i < me.pl->Width() - 2; i++){
    for(unsigned int j=0; j < me.pl->Height() - 5; j++){
      for(unsigned int k=0; k < me.pl->Width() - 2; k++)
	delete[] intermediary[i][j][k];
      delete[] intermediary[i][j];
    }
    delete[] intermediary[i];
  }
  delete[] intermediary;

  for(unsigned int i=0; i < me.pl->Width() - 2; i++){
    for(unsigned int j=0; j < me.pl->Height() - 5; j++){
      for(unsigned int k=0; k < me.pl->Width() - 2; k++)
	delete[] dist[i][j][k];
      delete[] dist[i][j];
    }
    delete[] dist[i];
  }
  delete[] dist;

  for(unsigned int i=0; i < me.pl->Width()-2; i++)
    delete[] vertices[i];
  delete[] vertices;
}


//wyliczanie sciezki
void AI::eval_path(){
  GraphAsMatrix g; //graf bedzie gesty (nawet pelny)
  
  //w razie, gdzy przeciwnkik wszedzie mial blizej potrzebne
  //sa dane najblizszego bonusa
  int my_min_dist = 100000;
  unsigned int closest_x = 0;
  unsigned int closest_y = 0;

  for(unsigned int x=0; x < me.pl->Width() - 2; x++){
    for(unsigned int y=0; y < me.pl->Height() - 5; y++){
      //sprawdzamy wszystkie pola planszy
      game_object * obj = me.pl->objects[x][y];
      if(obj == NULL)
	continue;
      if( obj->Type() == bonus_t ){
	int my_dist = distance( me.cur.X(), me.cur.Y(), x, y);
	int op_dist = distance( opponent->cur.X(), opponent->cur.Y(), x, y);

	if(my_dist < my_min_dist){
	  my_min_dist = my_dist;
	  closest_x = x;
	  closest_y = y;
	}

	if(my_dist < op_dist){
	  //jesli my mamy blizej to dodajemy wierzcholek do grafu
	  Vertex & v = g.AddVertex();
	  v.x = x;
	  v.y = y;
	  v.points = static_cast<bonus*>(obj)->Points();
	  v.op_dist = op_dist;
	}
      }
    }
  }
  
  if(g.NumberOfVertices() == 0){
    //mamy pecha
    next_x = closest_x;
    next_y = closest_y;
  }
  else{
    //robimy graf pelny. Wagi krawedzi to odleglosci
    for( Iterator<Vertex> & it1 = g.Vertices(); !it1.IsDone(); ++it1){
      for( Iterator<Vertex> & it2 = g.Vertices(); !it2.IsDone(); ++it2){
	if(!g.IsEdge((*it1).Number(), (*it2).Number()) && (*it1).Number() != (*it2).Number() ){
	  //jesli juz nie ma takiej krawedzi i nie robimy petli
	  Edge & e = g.AddEdge((*it1).Number(), (*it2).Number());
	  e.weight = distance((*it1).x, (*it1).y, (*it2).x, (*it2).y);
	}
      }
    }


    // najlepszej sciezki szukamy zmodyfikowanym algorytmem DFS.
    // tablica visited jest przekazywana przez wartosc (interesuje nas co odwiedzilismy
    // w danej sciezce)
    // dodatkowym warunkiem przerywajacym jest możliwość nie zdążenia do wierzchołka
    // przed graczem
    // szukamy sciezki o najwyzszym stosunku puntkow do jej dlugosci
    double best = 0;
    for( Iterator<Vertex> & it = g.Vertices(); !it.IsDone(); ++it){
      int dist = distance(me.cur.X(), me.cur.Y(), (*it).x, (*it).y);

      std::vector<bool> visited(g.NumberOfVertices());
      for(unsigned int i=0; i<visited.size(); i++)
	visited[i] = false;

      std::list<Vertex> current_path;

      dig(g, (*it).Number(), visited, dist, 0, best, current_path);
    }
  }
  me.pl->refresh();

  change = false;
  me.pl->refresh(false);
}


//kopanie w grafie (zmodyfikowany DFS)
void AI::dig(Graph & g, int V, std::vector<bool> visited, int dist, int sum, double & best, std::list<Vertex> current_path){
  visited[V] = true;
  sum += g.SelectVertex(V).points;
  current_path.push_back(g.SelectVertex(V));

  Iterator<Edge> & it = g.EmanatingEdges(V);
  while(!it.IsDone()){
    Vertex & X = (*it).Mate(V);
    //kopiemy tylko wierzcholki nie odwiedzone i takie, do ktorych zdazymy przed graczem
    if( !visited[X.Number()]  && dist + (*it).weight <= X.op_dist )
      dig(g, X.Number(), visited, dist + (*it).weight, sum, best, current_path);
    ++it;
  }

  double ratio = double(sum) / dist;
  if(ratio > best){
    best = ratio;
    path = current_path;
    next_x = current_path.front().x;
    next_y = current_path.front().y;
  }
}


//ruszanie sie
void AI::move(){
  if(change)
    eval_path();

  //tak naprawde chcemy isc tam, gdzie jest wierzcholek posredniczacy znaleziony przez alg. Floyda
  Vertex * v = intermediary[me.cur.X()][me.cur.Y()][next_x][next_y];
  if(v == NULL){
    next_intermediary_x = next_x;
    next_intermediary_y = next_y;
  }
  else{
    //szukamy wierzcholka do ktorego mamy isc
    while(distance(me.cur.X(), me.cur.Y(), v->x, v->y) > 1){
      v = intermediary[me.cur.X()][me.cur.Y()][v->x][v->y];
    }
    next_intermediary_x = v->x;
    next_intermediary_y = v->y;
  }

  //jesli dwa kierunki przyblizaja tak samo to losujemy sposrod nich
  //kod jest przystosowany do tego, że next_intermediary może być dalej niż 1 od kursora
  if(me.cur.X() != next_intermediary_x && me.cur.Y() != next_intermediary_y){
    if(rand()%2){
      if(me.cur.X() < next_intermediary_x)
	me.move(right);
      else if(me.cur.X() > next_intermediary_x)
	me.move(left);
    }
    else{
      if(me.cur.Y() < next_intermediary_y)
	me.move(down);
      else if(me.cur.Y() > next_intermediary_y)
	me.move(up);
    }
  }
  else if(me.cur.X() < next_intermediary_x)
    me.move(right);
  else if(me.cur.X() > next_intermediary_x)
    me.move(left);
  else if(me.cur.Y() < next_intermediary_y)
    me.move(down);
  else if(me.cur.Y() > next_intermediary_y)
    me.move(up);
}


//rysowanie swoich zamiarow
void AI::draw_path(){
  me.pl->clear();
  int i = 1;
  //rysujemy gdzie po kolei komputer chce isc
  for ( std::list<Vertex>::iterator it = path.begin(); it != path.end(); it++ )
    mvprintw(me.pl->Y0() + 4 + (*it).y, me.pl->X0() + 1 + (*it).x, "%i", i++);
  me.cur.draw();
  ::move(LINES-1, COLS-1); //kursor do rogu
}


//zwracanie dystansu
unsigned int AI::distance(unsigned int x1, unsigned int y1, unsigned int x2, unsigned int y2){
  //return ( abs(x1 - x2) + abs(y1 - y2) ); - wersja bez scian
  return dist[x1][y1][x2][y2];
}


//modelowanie planszy
void AI::create_playground_model(){
  model.MakeNull();
  unsigned int width = me.pl->Width() - 2;
  unsigned int height = me.pl->Height() - 5;

  //dodajemy wierzcholki
  for(unsigned int x=0; x < width; x++){
    for(unsigned int y=0; y < height; y++){
      if(me.pl->free(x,y)){
	Vertex & v = model .AddVertex();
	v.x = x;
	v.y = y;
	vertices[x][y] = &v;
      }
      else
	vertices[x][y] = NULL;
    }
  }

  //i krawedzie tam, gdzie sie da przejsc
  for(unsigned int x=0; x < width; x++){
    for(unsigned int y=0; y < height; y++){
      if(vertices[x][y] == NULL)
	continue;
      if(x < me.pl->Width() - 3 && vertices[x+1][y] != NULL)
	model.AddEdge( (*vertices[x][y]).Number(), (*vertices[x+1][y]).Number() );
      if(y < me.pl->Height() - 6 && vertices[x][y+1] != NULL)
	model.AddEdge( (*vertices[x][y]).Number(), (*vertices[x][y+1]).Number() );
    }
  }

  //ustalamy dystanse algorytmem Floyda
  //inicjalizacja
  for(unsigned int x1=0; x1 < width; x1++){
    for(unsigned int y1=0; y1 < height; y1++){
      for(unsigned int x2=0; x2 < width; x2++){
	for(unsigned int y2=0; y2 < height; y2++){
	  intermediary[x1][y1][x2][y2] = NULL;
	  if(x1==x2 && y1==y2)
	    dist[x1][y1][x2][y2] = 0;
	  else
	    dist[x1][y1][x2][y2] = 1000000;
	}
      }
    }
  }

  //ustalamy dystanse pomiedzy sasiadujacymi wierzcholkami
  for( Iterator<Edge> & it = model.Edges(); !it.IsDone(); ++it){
    dist[ (*it).V0().x ][ (*it).V0().y ][ (*it).V1().x ][ (*it).V1().y ] = 1;
    dist[ (*it).V1().x ][ (*it).V1().y ][ (*it).V0().x ][ (*it).V0().y ] = 1;
  }

  //algorytm Floyda
  for(unsigned int i=0; i < width*height; i++){
    loading_screen(double(i) / (width*height));
    for(unsigned int v=0; v < width*height; v++){
      for(unsigned int w=0; w < width*height; w++){
	int d = dist[ v%width ][ v/width ][ i%width ][ i/width ] + dist[ i%width ][ i/width ][ w%width ][ w/width ];

	if( d < dist[ v%width ][ v/width ][ w%width ][ w/width ] ){
	  dist[ v%width][ v/width][ w%width ][ w/width ] = dist[ w%width ][ w/width ][ v%width ][ v/width ] = d;
	  intermediary[ v%width ][ v/width ][ w%width ][ w/width ] = intermediary[ w%width ][ w/width ][ v%width ][ v/width ] = vertices[i%width][i/width];
	}
      }
    }
  }

  me.pl->refresh(); //ekran ladowania nabrudzil, trzeba naprawic
}

//ekran ladowania
void AI::loading_screen(double s){
  me.pl->clear();
  mvprintw(me.pl->Y0() + me.pl->Height() / 2, me.pl->X0() + me.pl->Width() / 2 - 11, "Calculating paths: %i%%", int(s*100));

  for(unsigned int x = me.pl->X0() + 3; x < me.pl->X0() + me.pl->Width() - 3; x++)
    mvaddch(LINES/2 + 2, x, '-');

  for(unsigned int x = me.pl->X0() + 3; x < me.pl->X0() + 3 + s*(me.pl->Width() - 6); x++)
    mvaddch(LINES/2 + 2, x, '#');

  ::move(LINES-1, COLS-1);

  refresh();
}
