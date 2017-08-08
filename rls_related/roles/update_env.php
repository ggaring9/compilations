# owner: releng
# description: tasks file for CMS Mobile base role deployments
---
- name: Copy env.php to current deployment
  template:
    src: env.php.j2
    dest: "{{ env_php }}"
  when: inventory_hostname in groups['webservers']
