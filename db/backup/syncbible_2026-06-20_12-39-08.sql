PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE book (
    id INTEGER PRIMARY KEY,
    name_en TEXT NOT NULL,
    name_cn TEXT NOT NULL,
    testament TEXT NOT NULL,
    order_index INTEGER NOT NULL
, abbr_en TEXT, abbr_cn TEXT);
INSERT INTO book VALUES(1,'Genesis','创世纪','Old',1,'Gen','创');
INSERT INTO book VALUES(2,'Exodus','出谷纪','Old',2,'Ex','出');
INSERT INTO book VALUES(3,'Leviticus','肋未纪','Old',3,'Lev','肋');
INSERT INTO book VALUES(4,'Numbers','户籍纪','Old',4,'Num','户');
INSERT INTO book VALUES(5,'Deuteronomy','申命纪','Old',5,'Dt','申');
INSERT INTO book VALUES(6,'Joshua','若苏厄书','Old',6,'Jos','苏');
INSERT INTO book VALUES(7,'Judges','民长纪','Old',7,'Jdg','民');
INSERT INTO book VALUES(8,'Ruth','卢德传','Old',8,'Ru','卢');
INSERT INTO book VALUES(9,'1 Samuel','撒慕尔纪上','Old',9,'1S','撒上');
INSERT INTO book VALUES(10,'2 Samuel','撒慕尔纪下','Old',10,'2S','撒下');
INSERT INTO book VALUES(11,'1 Kings','列王纪上','Old',11,'1K','列上');
INSERT INTO book VALUES(12,'2 Kings','列王纪下','Old',12,'2K','列下');
INSERT INTO book VALUES(13,'1 Chronicles','编年纪上','Old',13,'1Chr','编上');
INSERT INTO book VALUES(14,'2 Chronicles','编年纪下','Old',14,'2Chr','编下');
INSERT INTO book VALUES(15,'Ezra','厄斯德拉上','Old',15,'Ezra','厄上');
INSERT INTO book VALUES(16,'Nehemiah','厄斯德拉下(乃赫米雅)','Old',16,'Ne','厄下');
INSERT INTO book VALUES(17,'Tobit','多俾亚传','Old',17,'Tb','多');
INSERT INTO book VALUES(18,'Judith','友弟德传','Old',18,'Jdt','友');
INSERT INTO book VALUES(19,'Esther','艾斯德尔传','Old',19,'Es','艾');
INSERT INTO book VALUES(20,'1 Maccabees','玛加伯上','Old',20,'1Mac','加上');
INSERT INTO book VALUES(21,'2 Maccabees','玛加伯下','Old',21,'2Mac','加下');
INSERT INTO book VALUES(22,'Job','约伯传','Old',22,'Job','约');
INSERT INTO book VALUES(23,'Psalms','圣咏集','Old',23,'Ps','咏');
INSERT INTO book VALUES(24,'Proverbs','箴言篇','Old',24,'Pro','箴');
INSERT INTO book VALUES(25,'Ecclesiastes','训道篇','Old',25,'Ecl','训');
INSERT INTO book VALUES(26,'Song of Solomon','雅歌','Old',26,'Song','歌');
INSERT INTO book VALUES(27,'Wisdom','智慧篇','Old',27,'Wis','智');
INSERT INTO book VALUES(28,'Sirach','德训篇','Old',28,'Sir','德');
INSERT INTO book VALUES(29,'Isaiah','依撒意亚','Old',29,'Is','依');
INSERT INTO book VALUES(30,'Jeremiah','耶肋米亚','Old',30,'Jer','耶');
INSERT INTO book VALUES(31,'Lamentations','哀歌','Old',31,'Lm','哀');
INSERT INTO book VALUES(32,'Baruch','巴路克','Old',32,'Bar','巴');
INSERT INTO book VALUES(33,'Ezekiel','厄则克耳','Old',33,'Ezk','则');
INSERT INTO book VALUES(34,'Daniel','达尼尔','Old',34,'Dn','达');
INSERT INTO book VALUES(35,'Hosea','欧瑟亚','Old',35,'Hos','欧');
INSERT INTO book VALUES(36,'Joel','岳厄尔','Old',36,'Jl','岳');
INSERT INTO book VALUES(37,'Amos','亚毛斯','Old',37,'Am','亚');
INSERT INTO book VALUES(38,'Obadiah','亚北底亚','Old',38,'Ob','北');
INSERT INTO book VALUES(39,'Jonah','约纳','Old',39,'Jon','纳');
INSERT INTO book VALUES(40,'Micah','米该亚','Old',40,'Mic','米');
INSERT INTO book VALUES(41,'Nahum','纳鸿','Old',41,'Nh','鸿');
INSERT INTO book VALUES(42,'Habakkuk','哈巴谷','Old',42,'Hb','哈');
INSERT INTO book VALUES(43,'Zephaniah','索福尼亚','Old',43,'Zep','索');
INSERT INTO book VALUES(44,'Haggai','哈盖','Old',44,'Hg','盖');
INSERT INTO book VALUES(45,'Zechariah','匝加利亚','Old',45,'Zec','匝');
INSERT INTO book VALUES(46,'Malachi','玛拉基雅','Old',46,'Mal','拉');
INSERT INTO book VALUES(47,'Matthew','玛窦福音','New',47,'Mt','玛');
INSERT INTO book VALUES(48,'Mark','马尔谷福音','New',48,'Mk','谷');
INSERT INTO book VALUES(49,'Luke','路加福音','New',49,'Lk','路');
INSERT INTO book VALUES(50,'John','若望福音','New',50,'Jn','若');
INSERT INTO book VALUES(51,'Acts','宗徒大事录','New',51,'Acts','宗');
INSERT INTO book VALUES(52,'Romans','罗马书','New',52,'Rom','罗');
INSERT INTO book VALUES(53,'1 Corinthians','格林多前书','New',53,'1Cor','格前');
INSERT INTO book VALUES(54,'2 Corinthians','格林多后书','New',54,'2Cor','格后');
INSERT INTO book VALUES(55,'Galatians','迦拉达人书','New',55,'Gal','迦');
INSERT INTO book VALUES(56,'Ephesians','厄弗所书','New',56,'Eph','弗');
INSERT INTO book VALUES(57,'Philippians','斐理伯人书','New',57,'Phil','斐');
INSERT INTO book VALUES(58,'Colossians','哥罗森人书','New',58,'Col','哥');
INSERT INTO book VALUES(59,'1 Thessalonians','得撒洛尼前书','New',59,'1Thes','得前');
INSERT INTO book VALUES(60,'2 Thessalonians','得撒洛尼后书','New',60,'2Thes','得后');
INSERT INTO book VALUES(61,'1 Timothy','弟茂德前书','New',61,'1Tim','弟前');
INSERT INTO book VALUES(62,'2 Timothy','弟茂德后书','New',62,'2Tim','弟后');
INSERT INTO book VALUES(63,'Titus','弟铎书','New',63,'Tit','铎');
INSERT INTO book VALUES(64,'Philemon','费肋孟书','New',64,'Phlm','费');
INSERT INTO book VALUES(65,'Hebrews','希伯来人书','New',65,'Heb','希');
INSERT INTO book VALUES(66,'James','雅各伯书','New',66,'Jas','雅');
INSERT INTO book VALUES(67,'1 Peter','伯多禄前书','New',67,'1P','伯前');
INSERT INTO book VALUES(68,'2 Peter','伯多禄后书','New',68,'2P','伯后');
INSERT INTO book VALUES(69,'1 John','若望一书','New',69,'1Jn','若一');
INSERT INTO book VALUES(70,'2 John','若望二书','New',70,'2Jn','若二');
INSERT INTO book VALUES(71,'3 John','若望三书','New',71,'3Jn','若三');
INSERT INTO book VALUES(72,'Jude','犹达书','New',72,'Jd','犹');
INSERT INTO book VALUES(73,'Revelation','若望默示录','New',73,'Rev','默');
CREATE TABLE verse (
    id TEXT PRIMARY KEY,
    book_id INTEGER NOT NULL,
    chapter INTEGER NOT NULL,
    verse INTEGER NOT NULL,
    text_en TEXT NOT NULL,
    text_cn TEXT NOT NULL,
    FOREIGN KEY (book_id) REFERENCES book(id)
);
INSERT INTO verse VALUES('Mt.1.1',47,1,1,'An account of the genealogy of Jesus the Messiah, the son of David, the son of Abraham.','亚巴郎之子，达味之子耶稣基督的族谱：');
CREATE TABLE words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    verse_id TEXT NOT NULL,
    order_index INTEGER NOT NULL,
    word TEXT NOT NULL,
    type TEXT DEFAULT 'word',
    FOREIGN KEY (verse_id) REFERENCES verse(id)
);
INSERT INTO words VALUES(1,'Mt.1.1',1,'An','word');
INSERT INTO words VALUES(2,'Mt.1.1',2,'account','word');
INSERT INTO words VALUES(3,'Mt.1.1',3,'of','word');
INSERT INTO words VALUES(4,'Mt.1.1',4,'the','word');
INSERT INTO words VALUES(5,'Mt.1.1',5,'genealogy','word');
INSERT INTO words VALUES(6,'Mt.1.1',6,'of','word');
INSERT INTO words VALUES(7,'Mt.1.1',7,'Jesus','word');
INSERT INTO words VALUES(8,'Mt.1.1',8,'the','word');
INSERT INTO words VALUES(9,'Mt.1.1',9,'Messiah','word');
INSERT INTO words VALUES(10,'Mt.1.1',10,',','punct');
INSERT INTO words VALUES(11,'Mt.1.1',11,'the','word');
INSERT INTO words VALUES(12,'Mt.1.1',12,'son','word');
INSERT INTO words VALUES(13,'Mt.1.1',13,'of','word');
INSERT INTO words VALUES(14,'Mt.1.1',14,'David','word');
INSERT INTO words VALUES(15,'Mt.1.1',15,',','punct');
INSERT INTO words VALUES(16,'Mt.1.1',16,'the','word');
INSERT INTO words VALUES(17,'Mt.1.1',17,'son','word');
INSERT INTO words VALUES(18,'Mt.1.1',18,'of','word');
INSERT INTO words VALUES(19,'Mt.1.1',19,'Abraham','word');
INSERT INTO words VALUES(20,'Mt.1.1',20,'.','punct');
PRAGMA writable_schema=ON;
CREATE TABLE IF NOT EXISTS sqlite_sequence(name,seq);
DELETE FROM sqlite_sequence;
INSERT INTO sqlite_sequence VALUES('words',20);
PRAGMA writable_schema=OFF;
COMMIT;
