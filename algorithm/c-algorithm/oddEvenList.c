#include <stdio.h>
#include <string.h>
#include <stdlib.h>
/*
Given a singly linked list, group all odd nodes together followed by the even nodes. Please note here we are talking about the node number and not the value in the nodes.

You should try to do it in place. The program should run in O(1) space complexity and O(nodes) time complexity.

Example:
Given 1->2->3->4->5->NULL,
return 1->3->5->2->4->NULL.

Note:
The relative order inside both the even and odd groups should remain as it was in the input. 
The first node is considered odd, the second node even and so on ...}
  */

struct ListNode{
    int val;
    struct ListNode *next;
};

void insert_list( struct ListNode **head, struct ListNode *node)
{
    struct ListNode *p = *head;

    if(p == NULL){
        p = node;
    }
    else{
        node->next = p->next;
        p->next = node;
    }

    *head = p;
}

void print_list(struct ListNode *head)
{
    if(head == NULL){
        return;
    }
    struct ListNode *p = head;
    while(p){
        printf("%d ",p->val);
        p = p->next;
    }

    printf("\n");
}

struct ListNode* oddEvenList( struct ListNode* head )
{
    struct ListNode *ret = head;
    struct ListNode *p = head;
    struct ListNode *q = NULL;
    struct ListNode *odd_list = NULL;
    struct ListNode *even_list = NULL;
    struct ListNode *odd_p = NULL;
    struct ListNode *even_p = NULL;
    char flag = 'O';

    while(p){

        q = p->next;

        p->next = NULL;
        if( flag == 'O' ){
            if( odd_list== NULL ){
                odd_list = p;
                odd_p = p;
            }
            else{
                odd_p->next = p;
                odd_p = p;
            }

            flag = 'E';
        }
        else{
            if(even_list == NULL){
                even_list = p;
                even_p = p;
            }
            else{
                even_p->next = p;
                even_p = p;
            }

            flag = 'O';
        }

        p = q;

    }

    if(odd_p && even_list){
        odd_p->next = even_list;
    }

    return ret;
}

void init_node(struct ListNode **p, int val)
{
    *p = (struct ListNode *)malloc(sizeof(struct ListNode));
    (*p)->val = val;
    (*p)->next = NULL;
}

int main( int argc, char **argv )
{

    struct ListNode *head = NULL;
    struct ListNode *node = NULL;

    init_node( &node , 1);
    insert_list(&head, node);

    init_node( &node , 2);
    insert_list(&head, node);

    init_node( &node , 3);
    insert_list(&head, node);

    init_node( &node , 4);
    insert_list(&head, node);

    init_node( &node , 5);
    insert_list(&head, node);

    print_list(head);

    head = oddEvenList(head);
    print_list(head);

    return 0;
}
