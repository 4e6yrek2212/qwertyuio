Create table if not exists student(
	ID int primary key AUTO_INCREMENT,
    Name varchar(30),
    City varchar(30),
    Product varchar(30),
    Amount int,
    Sum int
);

Create table if not exists manager(
	ID int primary key AUTO_INCREMENT,
    Name varchar(30),
    Otdel varchar(30),
    Month varchar(30),
    Amount int,
    Sum int
);

Create table if not exists client(
	CustomerID int primary key AUTO_INCREMENT not null,
    Клиент varchar(30) not null,
    Город varchar(30) not null,
    OrderID int not null,
    Дата varchar(30) not null,
    Сумма int not null
);

Create table if not exists orders(
	OrderID int not null,
    ProductID int not null,
    Товар varchar(30) not null,
    Категория varchar(30) not null,
    Цена int not null,
    Количество int not null
);

insert into orders (OrderID,ProductID,Товар,Категория,Цена,Количество) values
(101, 201, "Товар 1", 101, 500, 1),
(102, 202, "Товар 2", 102, 1000, 2),
(103, 203, "Товар 3", 103, 1500, 3),
(104, 204, "Товар 4", 104, 2000, 4),
(105, 205, "Товар 5", 105, 2500, 5),
(106, 206, "Товар 6", 106, 3000, 6),
(107, 207, "Товар 7", 10, 3500, 7),
(108, 208, "Товар 8", 108, 4000, 8),
(109, 209, "Товар 9", 109, 4500, 9),
(110, 210, "Товар 10", 110, 5000, 10);

insert into client (CustomerID,Клиент,Город,OrderID,Дата,Сумма) values
(1, "Клиент 1", "Город 2", "101", "2026-05-01", 1000),
(2, "Клиент 2", "Город 3", "102", "2026-05-02", 2000),
(3, "Клиент 3", "Город 4", "103", "2026-05-03", 3000),
(4, "Клиент 4", "Город 1", "104", "2026-05-04", 4000),
(5, "Клиент 5", "Город 2", "105", "2026-05-05", 5000),
(6, "Клиент 6", "Город 3", "106", "2026-05-06", 6000),
(7, "Клиент 7", "Город 4", "107", "2026-05-07", 7000),
(8, "Клиент 8", "Город 1", "108", "2026-05-08", 8000),
(9, "Клиент 9", "Город 2", "109", "2026-05-09", 9000),
(10, "Клиент 10", "Город 3", "110", "2026-05-10", 10000);

insert into manager (ID,Name,Otdel,Month,Amount,Sum) values
(1, "Менеджер 2", "Отдел 2", "2026-01", 2, 1500),
(2, "Менеджер 3", "Отдел 3", "2026-02", 4, 3000),
(3, "Менеджер 4", "Отдел 1", "2026-03", 6, 4500),
(4, "Менеджер 1", "Отдел 2", "2026-04", 8, 6000),
(5, "Менеджер 2", "Отдел 3", "2026-05", 10, 7500),
(6, "Менеджер 3", "Отдел 1", "2026-06", 12, 9000),
(7, "Менеджер 4", "Отдел 2", "2026-07", 14, 10500),
(8, "Менеджер 1", "Отдел 3", "2026-08", 16, 12000),
(9, "Менеджер 2", "Отдел 1", "2026-09", 18, 13500),
(10, "Менеджер 3", "Отдел 2", "2026-10", 20, 15000);

insert into student (ID,Name,City,Product,Amount,Sum) values
(1, "Студент 1", "Город 2", "Товар 1", 2, 2400),
(2, "Студент 2", "Город 3", "Товар 2", 3, 3600),
(3, "Студент 3", "Город 4", "Товар 3", 4, 4800),
(4, "Студент 4", "Город 5", "Товар 4", 5, 6000),
(5, "Студент 5", "Город 1", "Товар 5", 6, 7200),
(6, "Студент 6", "Город 2", "Товар 6", 7, 8400),
(7, "Студент 7", "Город 3", "Товар 7", 8, 9600),
(8, "Студент 8", "Город 4", "Товар 8", 9, 10800),
(9, "Студент 9", "Город 5", "Товар 9", 10, 12000),
(10, "Студент 10", "Город 1", "Товар 10", 11, 13200);

-- 1
select * from student order by Sum desc;
-- 2
select * from student limit 3;
-- 3
select distinct city from student;
-- 4
select 
	Otdel, 
	sum(Amount) as total_am, 
	sum(Sum) as total_sum 
FROM manager 
group by Otdel;
-- 5
select 
	count(Name) as Total_name, 
    sum(Amount) as Total_amount, 
    AVG(Sum) as Average_sum 
from manager;
-- 6
select 
	Otdel, 
    sum(Amount) as Total_amount, 
    sum(Sum) as total_sum 
FROM manager
group by Otdel
Having sum(Sum) < 30000;
-- 7
select ID, Name, Amount, Sum from student
union
select ID, Name, Amount, Sum from manager;
-- 8
select 
	c.Клиент, 
    c.Город, 
    o.Товар, 
    o.Цена 
from client c 
inner join orders o ON c.OrderID = o.OrderID;
-- 9
select 
	c.Клиент, 
    c.Город, 
    o.Товар, 
    o.Цена 
from client c 
left join orders o ON c.OrderID = o.OrderID;
-- 10
select 
	c.Клиент, 
    c.Город, 
    o.Товар, 
    o.Цена 
from client c 
right join orders o ON c.OrderID = o.OrderID;
-- 11
select 
	c.Клиент, 
    c.Город, 
    o.Товар, 
    o.Цена 
from client c 
cross join orders o;
-- 12
select Name, City, Product 
from student
where City in (
	select City
    from student
    group by City
    Having sum(Sum) > 20000
);
-- 13
select * 
from client c
where exists (
	select Товар 
    from orders o 
    where o.OrderID = c.OrderID
);
-- 14
drop table if exists New_tab;
create table New_tab as 
select * from manager where Sum > 4000;
select * from New_tab;
-- 15
select 
	ID, 
	Name, 
	Otdel, 
	Amount, 
	sum(Amount) over() as total_amount,
	sum(Amount) over(partition by Otdel) as total_otdel_amount
from manager;
-- 16
select 
	ID, 
	Name, 
	Otdel, 
	Amount, 
	avg(Amount) over() as avg_dept_amount,
    Amount - AVG(Amount) over(partition by Otdel) as difference
from manager;
-- 17
select 
	Name,
	Otdel,
    sum(Amount) as total_am,
    RANK() over(partition by Otdel order by sum(Amount) desc) as Rank_in_Otdel
from manager
group by Name, Otdel;
-- 18
select
	ID,
    Name,
    Amount,
    LAG(Amount, 1, 0) over(order by ID) as prev_am,
    LEAD(Amount,1,0) over(order by ID) as next_am
from manager;
-- 19
select
	ID,
    Name,
    Amount,
    percent_rank() Over(order by Amount) as per_r_am
from manager;
-- 20
drop view if exists test;
create view test as 
select 
	Otdel,
    count(*) as num_of_s,
    sum(Amount) as tot_am
from manager
group by Otdel;
select * from test order by tot_am desc;
-- 21
start transaction;
update manager set Sum = Sum + 2 where ID = 1;
select * from manager where ID = 1;
commit;
-- 22
set transaction isolation level repeatable read;
start transaction;
select * from manager where ID = 1;
commit;
-- 23
drop temporary table if exists temp_man;
create temporary table temp_man as 
select 
	Otdel, 
    sum(Sum) as total_otd
from manager
group by Otdel;

select * from temp_man where total_otd > 1000;
-- 24
set @discount_rate = 0.10;
select 
	ID,
    Name,
    Sum,
    (Sum * @discount_rate) as Discount_Amount,
    (Sum - (Sum * @discount_rate)) as Final_Sum,
    IF(Sum >= 8000, "Крупный покупатель", "Обычный покупатель") as Status
from student;
-- 25
DELIMITER //

create procedure CalculateTopStudentsSum(IN max_id int, out total_sales int)
begin
	declare counter int default 1;
    declare current_sum int default 0;
	
    set total_sales = 0;
    
    While counter <= max_id DO
		select Sum into current_sum 
        from student 
        where ID = counter;
        
        set total_sales = total_sales + current_sum;
        set counter = counter + 1;
	end while;
end //
DELIMITER ;

CALL CalculateTopStudentsSum(5, @result);
SELECT @result AS Total_Sum_For_Top_5;